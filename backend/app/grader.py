from __future__ import annotations

import asyncio
import json
import os
import shlex
import tempfile
from collections import defaultdict
from pathlib import Path

import yaml

from .config import PASS_THRESHOLD
from .tasks_loader import DOMAIN_LABELS, Task


def _write_normalized_script(script: Path) -> Path:
    raw = script.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    with tempfile.NamedTemporaryFile(
        prefix=f"cka-{script.stem}-", suffix=".sh", delete=False
    ) as tf:
        tf.write(raw)
        tmp = Path(tf.name)
    tmp.chmod(0o755)
    return tmp


async def _exec_bash(
    cmd: list[str], env: dict[str, str], cwd: Path, timeout: int
) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        env=env,
        cwd=str(cwd),
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return 1, "script timed out"
    text = (out or b"").decode("utf-8", errors="replace")
    return proc.returncode or 0, text


async def _run_script(
    script: Path, env: dict[str, str], cwd: Path, timeout: int = 180
) -> tuple[int, str]:
    if not script.exists():
        return 1, f"missing script: {script}"
    tmp = _write_normalized_script(script)
    try:
        return await _exec_bash(["bash", str(tmp)], env, cwd, timeout)
    finally:
        tmp.unlink(missing_ok=True)


async def _run_check(
    script: Path, env: dict[str, str], cwd: Path, timeout: int = 45
) -> tuple[int, str, str]:
    """Run one grade check, keeping a bash xtrace separate from its output.

    The trace is how a failed ``grep -q`` or ``[`` test can still report the
    value that was actually on the cluster.
    """
    if not script.exists():
        return 1, f"missing script: {script}", ""
    tmp = _write_normalized_script(script)
    with tempfile.NamedTemporaryFile(
        prefix="cka-trace-", suffix=".log", delete=False
    ) as tf:
        trace_path = Path(tf.name)
    runner = Path(f"{tmp}.runner.sh")
    runner.write_text(
        "#!/usr/bin/env bash\n"
        f"exec 3>{shlex.quote(str(trace_path))}\n"
        "BASH_XTRACEFD=3\n"
        "set -x\n"
        f"source {shlex.quote(str(tmp))}\n",
        encoding="utf-8",
    )
    runner.chmod(0o755)
    try:
        code, out = await _exec_bash(["bash", str(runner)], env, cwd, timeout)
        trace = ""
        try:
            trace = trace_path.read_text(encoding="utf-8", errors="replace")[-80000:]
        except OSError:
            trace = ""
        return code, out, trace
    finally:
        tmp.unlink(missing_ok=True)
        runner.unlink(missing_ok=True)
        trace_path.unlink(missing_ok=True)


_NOISE_COMMANDS = {
    "set",
    "source",
    "export",
    "exec",
    "sleep",
    "exit",
    "true",
    "false",
    ":",
    "break",
    "continue",
    "local",
    "builtin",
    "return",
    "for",
    "while",
    "if",
    "then",
    "fi",
    "do",
    "done",
    "elif",
    "else",
}


def _trace_commands(trace: str) -> list[list[str]]:
    commands: list[list[str]] = []
    for raw in trace.splitlines():
        line = raw.rstrip()
        if not line.startswith("+"):
            continue
        rest = line.lstrip("+").strip()
        if not rest:
            continue
        try:
            args = shlex.split(rest)
        except ValueError:
            args = rest.split()
        if args:
            commands.append(args)
    return commands


def _assignment(args: list[str]) -> tuple[str, str] | None:
    if len(args) != 1 or "=" not in args[0]:
        return None
    name, value = args[0].split("=", 1)
    if not name.isidentifier() or name.startswith("BASH_"):
        return None
    return name, value


def _is_noise(args: list[str]) -> bool:
    if not args or args[0] in _NOISE_COMMANDS:
        return True
    assigned = _assignment(args)
    return assigned is not None and assigned[0].startswith("BASH_")


def _name_for(value: str, assignments: list[tuple[str, str]]) -> str | None:
    for name, found in reversed(assignments):
        if found == value:
            return name
    return None


def _inline(value: str, assignments: list[tuple[str, str]]) -> str:
    name = _name_for(value, assignments)
    shown = value if value != "" else "(empty)"
    if len(shown) > 160:
        shown = shown[:160] + "…"
    text = f"`{shown}`"
    if name:
        text += f" ({name})"
    return text


def _present_block(value: str) -> str:
    text = value.strip()
    if not text:
        return "(empty)"
    if text[0] in "{[":
        try:
            text = json.dumps(json.loads(text), indent=2)
        except json.JSONDecodeError:
            pass
    if len(text) > 1200:
        text = text[:1200] + "\n…"
    return text


def _k8s_errors(output: str) -> list[str]:
    found: list[str] = []
    for line in output.splitlines():
        text = line.strip()
        if not text:
            continue
        lower = text.lower()
        if (
            text.startswith("Error from server")
            or text.startswith("error:")
            or "timed out" in lower
            or text.startswith("Waiting for ")
        ):
            found.append(text)
    return found[-4:]


def _grep_query(args: list[str]) -> tuple[bool, str] | None:
    if not args or args[0] != "grep":
        return None
    quiet = False
    invert = False
    pattern: str | None = None
    index = 1
    while index < len(args):
        arg = args[index]
        if arg == "--":
            if index + 1 < len(args):
                pattern = args[index + 1]
            break
        if arg.startswith("-") and arg != "-":
            if "q" in arg:
                quiet = True
            if "v" in arg:
                invert = True
            if arg == "-e" and index + 1 < len(args):
                pattern = args[index + 1]
                index += 2
                continue
            index += 1
            continue
        pattern = arg
        break
    if not quiet or pattern is None:
        return None
    return invert, pattern


def _test_body(args: list[str]) -> list[str] | None:
    if args and args[0] == "[" and args[-1] == "]":
        return args[1:-1]
    if args and args[0] == "[[" and args[-1] == "]]":
        return args[1:-1]
    if args and args[0] == "test":
        return args[1:]
    return None


def _echo_text(args: list[str]) -> str | None:
    if not args or args[0] != "echo":
        return None
    parts = args[1:]
    if parts and parts[0] == "-n":
        parts = parts[1:]
    return " ".join(parts)


_DATA_COMMANDS = {"echo", "printf", "cat"}


def _is_assertion(args: list[str]) -> bool:
    return _test_body(args) is not None or _grep_query(args) is not None


def _failure_index(commands: list[list[str]]) -> tuple[int | None, list[list[str]]]:
    """Return the failing command and the nearby commands that produced its input.

    Bash traces the right-hand side of a pipeline first, so ``echo | grep -q``
    records grep and then echo. The echo still belongs to that failed check.
    """
    end = len(commands) - 1
    while end >= 0 and (_is_noise(commands[end]) or _assignment(commands[end])):
        end -= 1
    if end < 0:
        return None, []
    tail = commands[end]
    if not _is_assertion(tail) and tail[0] not in _DATA_COMMANDS:
        start = max(0, end - 6)
        return end, commands[start : end + 1]
    start = end
    while start >= 0 and (
        _is_noise(commands[start])
        or _assignment(commands[start]) is not None
        or _is_assertion(commands[start])
        or commands[start][0] in _DATA_COMMANDS
    ):
        start -= 1
    group = commands[start + 1 : end + 1]
    for offset in range(len(group) - 1, -1, -1):
        if _is_assertion(group[offset]):
            return start + 1 + offset, group
    return end, group


def explain_check_failure(output: str, trace: str) -> str:
    """Plain-language reason a grade check failed, from its output and xtrace."""
    if output.strip() == "script timed out":
        return "The check timed out before it finished."

    commands = _trace_commands(trace)
    fail_at, window = _failure_index(commands)
    assignments = [item for item in (_assignment(cmd) for cmd in window) if item]
    errors = _k8s_errors(output)

    if fail_at is None:
        if errors:
            return "\n".join(errors)
        tail = "\n".join(line.strip() for line in output.splitlines() if line.strip())
        return tail[-800:] or "The check failed."

    args = commands[fail_at]
    body = _test_body(args)
    if body is not None:
        if len(body) == 3 and body[1] in {"=", "==", "!=", "-eq", "-ne"}:
            left, op, right = body
            if op in {"!=", "-ne"}:
                message = (
                    f"Expected this not to be {_inline(right, assignments)}, "
                    f"but the cluster had {_inline(left, assignments)}."
                )
            else:
                message = (
                    f"Expected {_inline(right, assignments)}, "
                    f"but the cluster had {_inline(left, assignments)}."
                )
            return message
        if len(body) == 2 and body[0] in {"-z", "-n"}:
            value = body[1]
            if body[0] == "-z":
                return (
                    "Expected this to be empty, "
                    f"but the cluster had {_inline(value, assignments)}."
                )
            return (
                "Expected a value, "
                f"but the cluster had {_inline(value, assignments)}."
            )

    query = _grep_query(args)
    if query is not None:
        invert, pattern = query
        subject = ""
        echoes = [text for text in (_echo_text(cmd) for cmd in window) if text is not None]
        if echoes:
            subject = echoes[-1]
        if not subject and assignments:
            subject = assignments[-1][1]
        if invert:
            message = f"Expected this not to contain `{pattern}`, but it did."
        else:
            message = f"Expected this to contain `{pattern}`, but it did not."
        if subject:
            name = _name_for(subject, assignments)
            heading = "What was on the cluster"
            if name:
                heading += f" ({name})"
            message += f"\n{heading}:\n{_present_block(subject)}"
        return message

    if errors and args[0] in {"kubectl", "docker", "etcdctl", "crictl"}:
        command = " ".join(args)
        return "\n".join(errors + [f"Command: {command}"])

    if errors:
        return "\n".join(errors)

    command = " ".join(args)
    if len(command) > 300:
        command = command[:300] + "…"
    tail = "\n".join(
        line.strip() for line in output.splitlines() if line.strip()
    )[-500:]
    message = f"The check stopped on: {command}"
    if tail:
        message += f"\n{tail}"
    return message


async def run_setup(
    task: Task, kubeconfig: Path, cluster_name: str, home: Path | None = None
) -> None:
    env = {
        **os.environ,
        "KUBECONFIG": str(kubeconfig),
        "CLUSTER_NAME": cluster_name,
        "TASK_DIR": str(task.dir),
    }
    if home is not None:
        env["HOME"] = str(home)
        env["CANDIDATE_HOME"] = str(home)
    # Setups often wait up to 120s on rollout; keep headroom for image pulls.
    code, out = await _run_script(
        task.dir / "setup.sh", env, task.dir, timeout=300
    )
    if code != 0:
        raise RuntimeError(f"setup failed for {task.id}:\n{out}")


def _load_checks(task: Task) -> list[dict]:
    """Return checks with relative weights. Prefer assessment.yaml; else grade.sh=100."""
    assessment = task.dir / "assessment.yaml"
    if assessment.exists():
        with assessment.open(encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        checks = data.get("checks") or []
        if not checks:
            raise ValueError(f"{task.id}: assessment.yaml has no checks")
        return [
            {
                "id": str(c["id"]),
                "description": str(c.get("description") or c["id"]),
                "weight": int(c["weight"]),
                "script": task.dir / str(c["script"]),
            }
            for c in checks
        ]
    grade = task.dir / "grade.sh"
    return [
        {
            "id": "all",
            "description": "Full task",
            "weight": 100,
            "script": grade,
        }
    ]


def _scale_weights(raw_weights: list[int], target_total: int) -> list[int]:
    """Scale positive raw weights so they sum exactly to target_total."""
    total = sum(raw_weights)
    if total <= 0 or target_total <= 0:
        return [0] * len(raw_weights)
    scaled = [int(target_total * w / total) for w in raw_weights]
    # Fix rounding drift
    drift = target_total - sum(scaled)
    i = 0
    while drift != 0 and scaled:
        step = 1 if drift > 0 else -1
        scaled[i % len(scaled)] += step
        drift -= step
        i += 1
    return scaled


def load_answers(task: Task) -> str | None:
    path = task.dir / "answers.md"
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")


def skipped_task_result(task: Task) -> dict:
    """Score entry for a question never opened (no cluster / no attempt)."""
    return {
        "id": task.id,
        "title": task.title,
        "domain": task.domain,
        "domain_label": task.domain_label,
        "weight": task.weight,
        "passed": False,
        "earned": 0,
        "checks": [
            {
                "id": "skipped",
                "description": "Not attempted (question was not opened)",
                "weight": task.weight,
                "passed": False,
                "earned": 0,
                "failure": "This question was not opened, so nothing was graded.",
            }
        ],
        "output": "",
        "answers": load_answers(task),
    }


def assemble_score(tasks: list[Task], results_by_id: dict[str, dict]) -> dict:
    """Build final report from per-question results (missing → skipped)."""
    ordered = [
        results_by_id[t.id] if t.id in results_by_id else skipped_task_result(t)
        for t in tasks
    ]
    earned = 0
    domain_earned: dict[str, int] = defaultdict(int)
    domain_possible: dict[str, int] = defaultdict(int)
    for task, result in zip(tasks, ordered, strict=True):
        domain_possible[task.domain] += task.weight
        earned += result["earned"]
        domain_earned[task.domain] += result["earned"]

    domains = []
    for key, label in DOMAIN_LABELS.items():
        possible = domain_possible.get(key, 0)
        if possible == 0:
            continue
        domains.append(
            {
                "domain": key,
                "label": label,
                "earned": domain_earned.get(key, 0),
                "possible": possible,
            }
        )

    return {
        "score": earned,
        "pass": earned >= PASS_THRESHOLD,
        "pass_threshold": PASS_THRESHOLD,
        "results": ordered,
        "domains": domains,
    }


async def grade_task(
    task: Task,
    kubeconfig: Path,
    cluster_name: str,
    home: Path | None = None,
) -> dict:
    env = {
        **os.environ,
        "KUBECONFIG": str(kubeconfig),
        "CLUSTER_NAME": cluster_name,
        "TASK_DIR": str(task.dir),
    }
    if home is not None:
        env["HOME"] = str(home)
        env["CANDIDATE_HOME"] = str(home)
    checks_meta = _load_checks(task)
    scaled = _scale_weights(
        [c["weight"] for c in checks_meta], task.weight
    )
    check_results = []
    earned = 0
    outputs = []
    for meta, points in zip(checks_meta, scaled, strict=True):
        # Keep grade checks short — long kubectl waits blow past reverse proxies.
        code, out, trace = await _run_check(
            meta["script"], env, task.dir, timeout=45
        )
        passed = code == 0
        got = points if passed else 0
        earned += got
        outputs.append(out)
        failure = ""
        if not passed:
            failure = explain_check_failure(out, trace)[:2000]
        check_results.append(
            {
                "id": meta["id"],
                "description": meta["description"],
                "weight": points,
                "passed": passed,
                "earned": got,
                "output": out[-2000:],
                "failure": failure,
            }
        )

    return {
        "id": task.id,
        "title": task.title,
        "domain": task.domain,
        "domain_label": task.domain_label,
        "weight": task.weight,
        "passed": earned == task.weight and task.weight > 0,
        "earned": earned,
        "checks": check_results,
        "output": "\n".join(outputs)[-4000:],
        "answers": load_answers(task),
    }


async def grade_tasks(
    tasks: list[Task],
    kubeconfig: Path,
    cluster_name: str,
    on_progress=None,
) -> dict:
    """Grade all tasks. Optional on_progress(done: int, total: int, title: str)."""
    earned = 0
    domain_earned: dict[str, int] = defaultdict(int)
    domain_possible: dict[str, int] = defaultdict(int)
    for task in tasks:
        domain_possible[task.domain] += task.weight

    total = len(tasks)
    done = 0
    lock = asyncio.Lock()
    sem = asyncio.Semaphore(4)

    async def _one(task: Task) -> dict:
        nonlocal done
        async with sem:
            result = await grade_task(task, kubeconfig, cluster_name)
        async with lock:
            done += 1
            if on_progress is not None:
                on_progress(done, total, task.title)
        return result

    if on_progress is not None:
        on_progress(0, total, "Starting…")

    results = list(await asyncio.gather(*[_one(t) for t in tasks]))
    # Preserve exam order
    by_id = {r["id"]: r for r in results}
    ordered = [by_id[t.id] for t in tasks]

    for result in ordered:
        earned += result["earned"]
        domain_earned[result["domain"]] += result["earned"]

    domains = []
    for key, label in DOMAIN_LABELS.items():
        possible = domain_possible.get(key, 0)
        if possible == 0:
            continue
        domains.append(
            {
                "domain": key,
                "label": label,
                "earned": domain_earned.get(key, 0),
                "possible": possible,
            }
        )

    return {
        "score": earned,
        "pass": earned >= PASS_THRESHOLD,
        "pass_threshold": PASS_THRESHOLD,
        "results": ordered,
        "domains": domains,
    }
