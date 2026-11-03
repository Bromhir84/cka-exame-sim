from __future__ import annotations

import asyncio
import os
import tempfile
from collections import defaultdict
from pathlib import Path

from .config import PASS_THRESHOLD
from .tasks_loader import DOMAIN_LABELS, Task


async def _run_script(
    script: Path, env: dict[str, str], cwd: Path, timeout: int = 120
) -> tuple[int, str]:
    if not script.exists():
        return 1, f"missing script: {script}"
    # Normalize CRLF (Windows checkouts) so bash accepts `set -o pipefail`
    raw = script.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    with tempfile.NamedTemporaryFile(
        prefix=f"cka-{script.stem}-", suffix=".sh", delete=False
    ) as tf:
        tf.write(raw)
        tmp = Path(tf.name)
    tmp.chmod(0o755)
    try:
        proc = await asyncio.create_subprocess_exec(
            "bash",
            str(tmp),
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
    finally:
        tmp.unlink(missing_ok=True)


async def run_setup(task: Task, kubeconfig: Path, cluster_name: str) -> None:
    env = {
        **os.environ,
        "KUBECONFIG": str(kubeconfig),
        "CLUSTER_NAME": cluster_name,
        "TASK_DIR": str(task.dir),
    }
    code, out = await _run_script(task.dir / "setup.sh", env, task.dir)
    if code != 0:
        raise RuntimeError(f"setup failed for {task.id}:\n{out}")


async def grade_tasks(
    tasks: list[Task], kubeconfig: Path, cluster_name: str
) -> dict:
    env_base = {
        **os.environ,
        "KUBECONFIG": str(kubeconfig),
        "CLUSTER_NAME": cluster_name,
    }
    results = []
    earned = 0
    domain_earned: dict[str, int] = defaultdict(int)
    domain_possible: dict[str, int] = defaultdict(int)

    for task in tasks:
        domain_possible[task.domain] += task.weight
        env = {**env_base, "TASK_DIR": str(task.dir)}
        code, out = await _run_script(task.dir / "grade.sh", env, task.dir)
        passed = code == 0
        score = task.weight if passed else 0
        earned += score
        domain_earned[task.domain] += score
        results.append(
            {
                "id": task.id,
                "title": task.title,
                "domain": task.domain,
                "domain_label": task.domain_label,
                "weight": task.weight,
                "passed": passed,
                "earned": score,
                "output": out[-4000:],
            }
        )

    domains = []
    for key, label in DOMAIN_LABELS.items():
        possible = domain_possible.get(key, 0)
        if possible == 0:
            continue
        got = domain_earned.get(key, 0)
        domains.append(
            {
                "domain": key,
                "label": label,
                "earned": got,
                "possible": possible,
            }
        )

    return {
        "score": earned,
        "pass": earned >= PASS_THRESHOLD,
        "pass_threshold": PASS_THRESHOLD,
        "results": results,
        "domains": domains,
    }
