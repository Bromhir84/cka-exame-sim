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
from .grader import grade_tasks, run_setup
from .tasks_loader import Task, select_exam_tasks


class SessionStatus(str, Enum):
    PROVISIONING = "provisioning"
    READY = "ready"
    GRADING = "grading"
    DONE = "done"
    ERROR = "error"


PROVISION_STEPS = 7


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


_sessions: dict[str, ExamSession] = {}
_lock = asyncio.Lock()


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


async def _provision(session: ExamSession) -> None:
    try:
        session.workdir.mkdir(parents=True, exist_ok=True)
        kind_cfg = session.workdir / "kind.yaml"
        _kind_config(kind_cfg)

        _set_progress(session, 1, "Creating kind cluster…")
        code, out = await _run(
            [
                "kind",
                "create",
                "cluster",
                "--name",
                session.cluster_name,
                "--image",
                KIND_IMAGE,
                "--config",
                str(kind_cfg),
                "--kubeconfig",
                str(session.kubeconfig),
            ],
            timeout=300,
        )
        if code != 0:
            raise RuntimeError(f"kind create failed:\n{out}")

        _set_progress(session, 2, "Connecting to cluster API…")
        await _connect_to_kind_network()
        await _export_internal_kubeconfig(session.cluster_name, session.kubeconfig)
        await _wait_api(session.kubeconfig, timeout=180)

        _set_progress(session, 3, "Installing Calico networking…")
        await _install_calico(session.kubeconfig)

        _set_progress(session, 4, "Waiting for nodes to become Ready…")
        await _wait_nodes_ready(session.kubeconfig, timeout=300)

        _set_progress(session, 5, "Installing ingress controller…")
        await _install_ingress(session.kubeconfig)

        _set_progress(session, 6, "Preparing exam tasks…")
        for task in session.tasks:
            await run_setup(task, session.kubeconfig, session.cluster_name)

        # Optional noVNC desktop (best-effort; exam works without it)
        _set_progress(session, 7, "Starting remote desktop…")
        try:
            session.desktop_url = await start_desktop(
                session.id, session.kubeconfig, session.cluster_name
            )
        except Exception:  # noqa: BLE001
            session.desktop_url = None

        _set_progress(session, PROVISION_STEPS, "Ready")
        session.ends_at = datetime.now(timezone.utc) + timedelta(
            minutes=EXAM_DURATION_MINUTES
        )
        session.status = SessionStatus.READY
    except Exception as exc:  # noqa: BLE001
        session.status = SessionStatus.ERROR
        session.error = str(exc)
        session.progress_label = "Provisioning failed"
        await stop_desktop(session.id)
        await _destroy_cluster(session.cluster_name)


async def _destroy_cluster(cluster_name: str) -> None:
    await _run(["kind", "delete", "cluster", "--name", cluster_name], timeout=120)


async def create_session(domain: str | None = None) -> ExamSession:
    async with _lock:
        # MVP: only one active exam at a time to avoid resource fights
        for s in _sessions.values():
            if s.status in (SessionStatus.PROVISIONING, SessionStatus.READY, SessionStatus.GRADING):
                raise RuntimeError(
                    f"An exam session is already active ({s.id}, status={s.status.value})"
                )

    try:
        tasks = select_exam_tasks(domain=domain)
    except ValueError as exc:
        raise RuntimeError(str(exc)) from exc

    session_id = uuid.uuid4().hex[:10]
    cluster_name = f"cka-{session_id}"
    workdir = SESSIONS_DIR / session_id
    session = ExamSession(
        id=session_id,
        status=SessionStatus.PROVISIONING,
        cluster_name=cluster_name,
        workdir=workdir,
        kubeconfig=workdir / "kubeconfig",
        created_at=datetime.now(timezone.utc),
        tasks=tasks,
        domain=domain,
    )
    _sessions[session_id] = session
    asyncio.create_task(_provision(session))
    return session


async def end_session(session_id: str, cleanup: bool = True) -> dict:
    session = get_session(session_id)
    if not session:
        raise KeyError("session not found")
    if session.status == SessionStatus.DONE and session.score:
        return session.score
    if session.status == SessionStatus.PROVISIONING:
        raise RuntimeError("session still provisioning")
    if session.status == SessionStatus.ERROR:
        raise RuntimeError(session.error or "session failed")

    session.status = SessionStatus.GRADING
    try:
        score = await grade_tasks(session.tasks, session.kubeconfig, session.cluster_name)
        session.score = score
        session.status = SessionStatus.DONE
        return score
    finally:
        if cleanup:
            await destroy_session(session_id, delete_record=False)


async def destroy_session(session_id: str, delete_record: bool = True) -> None:
    session = get_session(session_id)
    if not session:
        return
    await stop_desktop(session_id)
    session.desktop_url = None
    await _destroy_cluster(session.cluster_name)
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
    if session.status == SessionStatus.READY:
        percent = 100
    elif session.status == SessionStatus.PROVISIONING:
        # Credit completed prior steps; current step is in-flight
        percent = int(round(100 * max(0, session.progress_step - 1) / total))
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
        "progress": {
            "step": session.progress_step,
            "total": session.progress_total,
            "label": session.progress_label,
            "percent": percent,
        },
    }
