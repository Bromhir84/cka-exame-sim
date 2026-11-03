from __future__ import annotations

import asyncio
import shutil
import socket
import textwrap
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path

from .config import EXAM_DURATION_MINUTES, KIND_IMAGE, SESSIONS_DIR
from .desktop import start_desktop, stop_desktop
from .grader import assemble_score, grade_task, run_setup
from .tasks_loader import Task, select_exam_tasks


class SessionStatus(str, Enum):
    PROVISIONING = "provisioning"
    SWITCHING = "switching"  # pausing / creating / reconnecting question clusters
    READY = "ready"
    GRADING = "grading"
    DONE = "done"
    ERROR = "error"


PROVISION_STEPS = 7
RECONNECT_STEPS = 3


@dataclass
class TaskClusterState:
    """Per-question kind cluster kept alive for the exam so work survives switches."""

    cluster_name: str
    kubeconfig: Path


@dataclass
class ExamSession:
    id: str
    status: SessionStatus
    cluster_name: str
    workdir: Path
    kubeconfig: Path
    created_at: datetime
    ends_at: datetime | None = None
    error: str | None = None
    score: dict | None = None
    tasks: list[Task] = field(default_factory=list)
    domain: str | None = None  # None = full multi-domain exam
    desktop_url: str | None = None
    progress_step: int = 0
    progress_total: int = PROVISION_STEPS
    progress_label: str = "Queued…"
    active_task_id: str | None = None
    # Living clusters keyed by task id (work is preserved across Previous/Next)
    task_clusters: dict[str, TaskClusterState] = field(default_factory=dict)
    # Graded results keyed by task id (filled at End Exam)
    task_results: dict[str, dict] = field(default_factory=dict)
    switch_lock: asyncio.Lock = field(default_factory=asyncio.Lock)


_sessions: dict[str, ExamSession] = {}
_lock = asyncio.Lock()


def _task_index(session: ExamSession, task_id: str) -> int:
    for i, t in enumerate(session.tasks):
        if t.id == task_id:
            return i
    raise KeyError(task_id)


def _cluster_name_for(session: ExamSession, task_id: str) -> str:
    return f"cka-{session.id}-{_task_index(session, task_id):02d}"


def _kubeconfig_for(session: ExamSession, task_id: str) -> Path:
    return session.workdir / f"kubeconfig-{task_id}"


def _bind_active_cluster(session: ExamSession, task_id: str) -> TaskClusterState:
    state = session.task_clusters[task_id]
    session.active_task_id = task_id
    session.cluster_name = state.cluster_name
    session.kubeconfig = state.kubeconfig
    return state


def _get_task(session: ExamSession, task_id: str) -> Task:
    for t in session.tasks:
        if t.id == task_id:
            return t
    raise KeyError(task_id)


def _set_progress(session: ExamSession, step: int, label: str) -> None:
    """step is 1..PROVISION_STEPS while working; percent reflects completed prior steps."""
    session.progress_step = step
    session.progress_total = PROVISION_STEPS
    session.progress_label = label


def get_session(session_id: str) -> ExamSession | None:
    return _sessions.get(session_id)


def list_sessions() -> list[ExamSession]:
    return list(_sessions.values())


async def _run(cmd: list[str], timeout: int = 600) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return 1, f"command timed out: {' '.join(cmd)}"
    return proc.returncode or 0, (out or b"").decode("utf-8", errors="replace")


def _kind_config(path: Path) -> None:
    # No hostPort mappings: publishing fixed host ports (8080/8443) collides with
    # other local services and leftover containers. Ingress still works in-cluster
    # via the kind ingress-nginx hostPorts on the node; use kubectl/curl from the
    # exam terminal (not localhost:8080 on the Docker host).
    path.write_text(
        textwrap.dedent(
            """\
            kind: Cluster
            apiVersion: kind.x-k8s.io/v1alpha4
            nodes:
              - role: control-plane
                kubeadmConfigPatches:
                  - |
                    kind: InitConfiguration
                    nodeRegistration:
                      kubeletExtraArgs:
                        node-labels: "ingress-ready=true"
              - role: worker
            networking:
              disableDefaultCNI: true
              podSubnet: "192.168.0.0/16"
            """
        ),
        encoding="utf-8",
    )


async def _connect_to_kind_network() -> None:
    """Allow this backend container to reach the kind control-plane over the kind bridge."""
    container = socket.gethostname()
    code, out = await _run(
        ["docker", "network", "connect", "kind", container], timeout=30
    )
    if code != 0 and "already exists" not in out.lower() and "already connected" not in out.lower():
        # Non-fatal if network missing yet — kind create should have made it
        if "not found" in out.lower():
            return
        raise RuntimeError(f"failed to join kind network:\n{out}")


async def _export_internal_kubeconfig(cluster_name: str, kubeconfig: Path) -> None:
    code, out = await _run(
        [
            "kind",
            "export",
            "kubeconfig",
            "--name",
            cluster_name,
            "--internal",
            "--kubeconfig",
            str(kubeconfig),
        ],
        timeout=60,
    )
    if code != 0:
        raise RuntimeError(f"kind export kubeconfig --internal failed:\n{out}")


async def _wait_api(kubeconfig: Path, timeout: int = 120) -> None:
    deadline = asyncio.get_event_loop().time() + timeout
    last = ""
    while asyncio.get_event_loop().time() < deadline:
        code, out = await _run(
            ["kubectl", "--kubeconfig", str(kubeconfig), "get", "--raw", "/healthz"],
            timeout=20,
        )
        last = out
        if code == 0:
            return
        await asyncio.sleep(2)
    raise RuntimeError(f"kubernetes API did not become ready:\n{last}")


async def _wait_nodes_ready(kubeconfig: Path, timeout: int = 180) -> None:
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        code, out = await _run(
            [
                "kubectl",
                "--kubeconfig",
                str(kubeconfig),
                "get",
                "nodes",
                "--no-headers",
            ],
            timeout=30,
        )
        if code == 0 and out.strip():
            lines = [ln for ln in out.strip().splitlines() if ln.strip()]
            if lines and all(" Ready" in ln or ln.split()[1] == "Ready" for ln in lines):
                return
        await asyncio.sleep(3)
    raise RuntimeError("nodes did not become Ready in time")


async def _install_calico(kubeconfig: Path) -> None:
    code, out = await _run(
        [
            "kubectl",
            "--kubeconfig",
            str(kubeconfig),
            "apply",
            "--validate=false",
            "-f",
            "https://raw.githubusercontent.com/projectcalico/calico/v3.28.2/manifests/calico.yaml",
        ],
        timeout=180,
    )
    if code != 0:
        raise RuntimeError(f"failed to install Calico:\n{out}")
    # wait for calico pods
    deadline = asyncio.get_event_loop().time() + 240
    while asyncio.get_event_loop().time() < deadline:
        code, out = await _run(
            [
                "kubectl",
                "--kubeconfig",
                str(kubeconfig),
                "-n",
                "kube-system",
                "wait",
                "--for=condition=Ready",
                "pod",
                "-l",
                "k8s-app=calico-node",
                "--timeout=30s",
            ],
            timeout=60,
        )
        if code == 0:
            return
        await asyncio.sleep(5)
    raise RuntimeError("Calico did not become ready")


async def _install_ingress(kubeconfig: Path) -> None:
    code, out = await _run(
        [
            "kubectl",
            "--kubeconfig",
            str(kubeconfig),
            "apply",
            "-f",
            "https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.3/deploy/static/provider/kind/deploy.yaml",
        ],
        timeout=180,
    )
    if code != 0:
        raise RuntimeError(f"failed to install ingress-nginx:\n{out}")
    await _run(
        [
            "kubectl",
            "--kubeconfig",
            str(kubeconfig),
            "-n",
            "ingress-nginx",
            "wait",
            "--namespace",
            "ingress-nginx",
            "--for=condition=Ready",
            "pod",
            "-l",
            "app.kubernetes.io/component=controller",
            "--timeout=180s",
        ],
        timeout=200,
    )


async def _cluster_container_ids(cluster_name: str) -> list[str]:
    if not cluster_name:
        return []
    code, out = await _run(
        [
            "docker",
            "ps",
            "-q",
            "--filter",
            f"label=io.x-k8s.kind.cluster={cluster_name}",
        ],
        timeout=30,
    )
    if code != 0:
        return []
    return [line.strip() for line in out.splitlines() if line.strip()]


async def _set_cluster_paused(cluster_name: str, paused: bool) -> None:
    """Freeze inactive question clusters to cut CPU while keeping RAM state."""
    ids = await _cluster_container_ids(cluster_name)
    if not ids:
        return
    action = "pause" if paused else "unpause"
    await _run(["docker", action, *ids], timeout=60)


async def _destroy_cluster(cluster_name: str) -> None:
    if not cluster_name:
        return
    # Unpause first so kind delete can talk to the containers cleanly
    await _set_cluster_paused(cluster_name, False)
    await _run(["kind", "delete", "cluster", "--name", cluster_name], timeout=120)


async def _destroy_all_clusters(session: ExamSession) -> None:
    names = {state.cluster_name for state in session.task_clusters.values()}
    if session.cluster_name:
        names.add(session.cluster_name)
    for name in sorted(names):
        await _destroy_cluster(name)
    session.task_clusters.clear()


async def _start_session_desktop(session: ExamSession) -> None:
    try:
        session.desktop_url = await start_desktop(
            session.id, session.kubeconfig, session.cluster_name
        )
    except Exception:  # noqa: BLE001
        session.desktop_url = None


async def _provision_task_cluster(session: ExamSession, task: Task) -> None:
    """Create a dedicated kind cluster and run setup for a single question."""
    cluster_name = _cluster_name_for(session, task.id)
    kubeconfig = _kubeconfig_for(session, task.id)
    session.workdir.mkdir(parents=True, exist_ok=True)
    session.cluster_name = cluster_name
    session.kubeconfig = kubeconfig
    session.active_task_id = task.id

    kind_cfg = session.workdir / "kind.yaml"
    _kind_config(kind_cfg)

    # Remove leftover cluster with this name only (other questions stay intact)
    await _destroy_cluster(cluster_name)

    _set_progress(session, 1, f"Creating cluster for “{task.title}”…")
    code, out = await _run(
        [
            "kind",
            "create",
            "cluster",
            "--name",
            cluster_name,
            "--image",
            KIND_IMAGE,
            "--config",
            str(kind_cfg),
            "--kubeconfig",
            str(kubeconfig),
        ],
        timeout=300,
    )
    if code != 0:
        raise RuntimeError(f"kind create failed:\n{out}")

    _set_progress(session, 2, "Connecting to cluster API…")
    await _connect_to_kind_network()
    await _export_internal_kubeconfig(cluster_name, kubeconfig)
    await _wait_api(kubeconfig, timeout=180)

    _set_progress(session, 3, "Installing Calico networking…")
    await _install_calico(kubeconfig)

    _set_progress(session, 4, "Waiting for nodes to become Ready…")
    await _wait_nodes_ready(kubeconfig, timeout=300)

    _set_progress(session, 5, "Installing ingress controller…")
    await _install_ingress(kubeconfig)

    _set_progress(session, 6, f"Preparing question “{task.title}”…")
    await run_setup(task, kubeconfig, cluster_name)

    session.task_clusters[task.id] = TaskClusterState(
        cluster_name=cluster_name, kubeconfig=kubeconfig
    )

    _set_progress(session, 7, "Starting remote desktop…")
    await _start_session_desktop(session)
    _set_progress(session, PROVISION_STEPS, "Ready")


async def _reconnect_task_cluster(session: ExamSession, task: Task) -> None:
    """Resume a previously opened question cluster without wiping student work."""
    state = _bind_active_cluster(session, task.id)
    session.progress_total = RECONNECT_STEPS
    session.progress_step = 1
    session.progress_label = f"Resuming cluster for “{task.title}”…"

    await _set_cluster_paused(state.cluster_name, False)
    await _connect_to_kind_network()

    session.progress_step = 2
    session.progress_label = "Waiting for cluster API…"
    await _wait_api(state.kubeconfig, timeout=120)

    session.progress_step = 3
    session.progress_label = "Starting remote desktop…"
    await _start_session_desktop(session)
    session.progress_label = "Ready"


async def _provision(session: ExamSession) -> None:
    """Initial exam start: provision cluster for the first question only."""
    try:
        if not session.active_task_id:
            session.active_task_id = session.tasks[0].id
        task = _get_task(session, session.active_task_id)
        await _provision_task_cluster(session, task)
        session.ends_at = datetime.now(timezone.utc) + timedelta(
            minutes=EXAM_DURATION_MINUTES
        )
        session.status = SessionStatus.READY
    except Exception as exc:  # noqa: BLE001
        session.status = SessionStatus.ERROR
        session.error = str(exc)
        session.progress_label = "Provisioning failed"
        await stop_desktop(session.id)
        await _destroy_all_clusters(session)


async def _grade_task_cluster(session: ExamSession, task_id: str) -> None:
    state = session.task_clusters.get(task_id)
    if not state:
        return
    task = _get_task(session, task_id)
    await _set_cluster_paused(state.cluster_name, False)
    await _wait_api(state.kubeconfig, timeout=60)
    result = await grade_task(task, state.kubeconfig, state.cluster_name)
    session.task_results[task.id] = result


async def create_session(domain: str | None = None) -> ExamSession:
    async with _lock:
        for s in _sessions.values():
            if s.status in (
                SessionStatus.PROVISIONING,
                SessionStatus.SWITCHING,
                SessionStatus.READY,
                SessionStatus.GRADING,
            ):
                raise RuntimeError(
                    f"An exam session is already active ({s.id}, status={s.status.value})"
                )

    try:
        tasks = select_exam_tasks(domain=domain)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    session_id = uuid.uuid4().hex[:10]
    workdir = SESSIONS_DIR / session_id
    first = tasks[0]
    session = ExamSession(
        id=session_id,
        status=SessionStatus.PROVISIONING,
        cluster_name="",
        workdir=workdir,
        kubeconfig=workdir / f"kubeconfig-{first.id}",
        created_at=datetime.now(timezone.utc),
        tasks=tasks,
        domain=domain,
        active_task_id=first.id,
    )
    session.cluster_name = _cluster_name_for(session, first.id)
    _sessions[session_id] = session
    asyncio.create_task(_provision(session))
    return session


async def _switch_task(session_id: str, task_id: str) -> None:
    session = get_session(session_id)
    if not session:
        return
    async with session.switch_lock:
        session = get_session(session_id)
        if not session:
            return
        if session.active_task_id == task_id and session.status == SessionStatus.READY:
            return
        session.status = SessionStatus.SWITCHING
        session.error = None
        leaving_id = session.active_task_id
        try:
            session.progress_step = 1
            session.progress_label = "Parking current question cluster…"
            await stop_desktop(session.id)
            session.desktop_url = None
            if leaving_id and leaving_id in session.task_clusters:
                leaving = session.task_clusters[leaving_id]
                await _set_cluster_paused(leaving.cluster_name, True)

            task = _get_task(session, task_id)
            if task_id in session.task_clusters:
                await _reconnect_task_cluster(session, task)
            else:
                await _provision_task_cluster(session, task)
            session.status = SessionStatus.READY
        except Exception as exc:  # noqa: BLE001
            session.status = SessionStatus.ERROR
            session.error = str(exc)
            session.progress_label = "Question switch failed"
            await stop_desktop(session.id)
            # Keep other question clusters; only drop a half-created target if needed
            if task_id not in session.task_clusters and session.cluster_name:
                await _destroy_cluster(session.cluster_name)


async def activate_task(session_id: str, task_id: str) -> ExamSession:
    """Start switching to another question (async). Poll session until status=ready."""
    session = get_session(session_id)
    if not session:
        raise KeyError("session not found")
    if session.status == SessionStatus.SWITCHING:
        return session
    if session.status != SessionStatus.READY:
        raise RuntimeError(
            f"cannot switch questions while status={session.status.value}"
        )
    _get_task(session, task_id)
    if task_id in session.task_results:
        raise RuntimeError(
            "that question is already finished (grade saved, cluster removed)"
        )
    if session.active_task_id == task_id:
        return session

    session.status = SessionStatus.SWITCHING
    session.error = None
    returning = task_id in session.task_clusters
    session.progress_step = 1
    session.progress_total = RECONNECT_STEPS if returning else PROVISION_STEPS
    session.progress_label = (
        "Resuming previous question cluster…"
        if returning
        else "Provisioning next question cluster…"
    )
    asyncio.create_task(_switch_task(session_id, task_id))
    return session


FINISH_STEPS = 4


def _next_unfinished_task_id(session: ExamSession, after_id: str) -> str | None:
    """Prefer the next unfinished question after after_id, else any unfinished."""
    n = len(session.tasks)
    start = 0
    try:
        start = _task_index(session, after_id) + 1
    except KeyError:
        start = 0
    for offset in range(n):
        task = session.tasks[(start + offset) % n]
        if task.id not in session.task_results:
            return task.id
    return None


async def _finish_task_job(session_id: str, task_id: str) -> None:
    session = get_session(session_id)
    if not session:
        return
    async with session.switch_lock:
        session = get_session(session_id)
        if not session:
            return
        session.status = SessionStatus.SWITCHING
        session.error = None
        was_active = session.active_task_id == task_id
        try:
            session.progress_total = FINISH_STEPS
            session.progress_step = 1
            session.progress_label = "Grading question (result hidden until End Exam)…"
            await _grade_task_cluster(session, task_id)

            session.progress_step = 2
            session.progress_label = "Stopping desktop…"
            if was_active:
                await stop_desktop(session.id)
                session.desktop_url = None

            session.progress_step = 3
            session.progress_label = "Removing question cluster…"
            state = session.task_clusters.pop(task_id, None)
            if state:
                await _destroy_cluster(state.cluster_name)
            elif was_active and session.cluster_name:
                await _destroy_cluster(session.cluster_name)

            session.progress_step = 4
            if was_active:
                next_id = _next_unfinished_task_id(session, task_id)
                if next_id:
                    session.progress_label = "Opening next unfinished question…"
                    task = _get_task(session, next_id)
                    if next_id in session.task_clusters:
                        await _reconnect_task_cluster(session, task)
                    else:
                        await _provision_task_cluster(session, task)
                else:
                    session.active_task_id = None
                    session.cluster_name = ""
                    session.progress_label = (
                        "Question finished — use End Exam for your score"
                    )
            else:
                session.progress_label = "Question finished (grade saved)"
            session.status = SessionStatus.READY
        except Exception as exc:  # noqa: BLE001
            session.status = SessionStatus.ERROR
            session.error = str(exc)
            session.progress_label = "Finish question failed"
            if was_active:
                await stop_desktop(session.id)
                session.desktop_url = None


async def finish_task(session_id: str, task_id: str) -> ExamSession:
    """Grade one question, save result quietly, destroy its cluster (async)."""
    session = get_session(session_id)
    if not session:
        raise KeyError("session not found")
    if session.status == SessionStatus.SWITCHING:
        return session
    if session.status != SessionStatus.READY:
        raise RuntimeError(
            f"cannot finish a question while status={session.status.value}"
        )
    _get_task(session, task_id)
    if task_id in session.task_results:
        raise RuntimeError("that question is already finished")
    if task_id not in session.task_clusters:
        raise RuntimeError("open this question’s cluster before finishing it")

    session.status = SessionStatus.SWITCHING
    session.error = None
    session.progress_step = 1
    session.progress_total = FINISH_STEPS
    session.progress_label = "Finishing question…"
    asyncio.create_task(_finish_task_job(session_id, task_id))
    return session


async def _cleanup_after_exam(session_id: str) -> None:
    try:
        await destroy_session(session_id, delete_record=False)
    except Exception:  # noqa: BLE001
        pass


async def _grade_session(session_id: str, cleanup: bool) -> None:
    session = get_session(session_id)
    if not session:
        return

    try:
        # Already-finished questions keep their saved results; only grade living clusters
        remaining = [t for t in session.tasks if t.id in session.task_clusters]
        pre_finished = len(session.task_results)
        total = max(1, len(remaining))
        session.progress_total = total
        session.progress_step = 0
        if pre_finished:
            session.progress_label = (
                f"Using {pre_finished} saved finish result(s); grading open clusters…"
            )
        else:
            session.progress_label = "Grading opened questions…"

        for i, task in enumerate(remaining, start=1):
            session.progress_step = i - 1
            session.progress_label = f"Grading “{task.title}” ({i}/{len(remaining)})…"
            try:
                await _grade_task_cluster(session, task.id)
            except Exception:  # noqa: BLE001
                # Keep going so one bad cluster does not wipe the whole report
                pass

        session.progress_step = total
        session.progress_label = "Assembling score report…"
        session.score = assemble_score(session.tasks, session.task_results)
        session.progress_label = "Grading complete"
        session.status = SessionStatus.DONE
        if cleanup:
            asyncio.create_task(_cleanup_after_exam(session_id))
    except Exception as exc:  # noqa: BLE001
        session.error = str(exc)
        session.status = SessionStatus.READY


async def start_end_session(session_id: str, cleanup: bool = True) -> ExamSession:
    session = get_session(session_id)
    if not session:
        raise KeyError("session not found")
    if session.status == SessionStatus.DONE and session.score:
        return session
    if session.status in (SessionStatus.PROVISIONING, SessionStatus.SWITCHING):
        raise RuntimeError("session still provisioning / switching questions")
    if session.status == SessionStatus.ERROR:
        raise RuntimeError(session.error or "session failed")
    if session.status == SessionStatus.GRADING:
        return session

    session.status = SessionStatus.GRADING
    session.error = None
    session.progress_step = 0
    session.progress_total = max(1, len(session.task_clusters) or len(session.tasks))
    session.progress_label = "Starting grading…"
    asyncio.create_task(_grade_session(session_id, cleanup))
    return session


async def end_session(session_id: str, cleanup: bool = True) -> dict:
    session = await start_end_session(session_id, cleanup=cleanup)
    if session.status == SessionStatus.DONE and session.score:
        return session.score
    deadline = asyncio.get_event_loop().time() + 600
    while asyncio.get_event_loop().time() < deadline:
        session = get_session(session_id)
        if not session:
            raise RuntimeError("session disappeared while grading")
        if session.status == SessionStatus.DONE and session.score:
            return session.score
        if session.status == SessionStatus.READY and session.error:
            raise RuntimeError(session.error)
        await asyncio.sleep(0.5)
    raise RuntimeError("grading timed out")


async def destroy_session(session_id: str, delete_record: bool = True) -> None:
    session = get_session(session_id)
    if not session:
        return
    await stop_desktop(session_id)
    session.desktop_url = None
    await _destroy_all_clusters(session)
    if session.workdir.exists():
        shutil.rmtree(session.workdir, ignore_errors=True)
    if delete_record:
        _sessions.pop(session_id, None)


def session_public(session: ExamSession) -> dict:
    now = datetime.now(timezone.utc)
    remaining = None
    if session.ends_at:
        remaining = max(0, int((session.ends_at - now).total_seconds()))
    total = max(1, session.progress_total)
    if session.status == SessionStatus.DONE:
        percent = 100
    elif session.status in (SessionStatus.PROVISIONING, SessionStatus.SWITCHING):
        percent = int(round(100 * max(0, session.progress_step - 1) / total))
    elif session.status == SessionStatus.GRADING:
        percent = int(round(100 * session.progress_step / total))
    elif session.status == SessionStatus.READY:
        percent = 100
    else:
        percent = int(round(100 * session.progress_step / total))
    return {
        "session_id": session.id,
        "status": session.status.value,
        "cluster_name": session.cluster_name,
        "created_at": session.created_at.isoformat(),
        "ends_at": session.ends_at.isoformat() if session.ends_at else None,
        "remaining_seconds": remaining,
        "error": session.error,
        "score": session.score,
        "task_ids": [t.id for t in session.tasks],
        "domain": session.domain,
        "desktop_url": session.desktop_url,
        "active_task_id": session.active_task_id,
        "opened_task_ids": sorted(session.task_clusters.keys()),
        # IDs only — scores stay hidden until End Exam (status=done)
        "finished_task_ids": sorted(session.task_results.keys()),
        "progress": {
            "step": session.progress_step,
            "total": session.progress_total,
            "label": session.progress_label,
            "percent": percent,
        },
    }
