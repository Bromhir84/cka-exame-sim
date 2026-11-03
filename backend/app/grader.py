from __future__ import annotations

import asyncio
import os
import tempfile
from collections import defaultdict
from pathlib import Path

import yaml

from .config import PASS_THRESHOLD
from .tasks_loader import DOMAIN_LABELS, Task


async def _run_script(
    script: Path, env: dict[str, str], cwd: Path, timeout: int = 180
) -> tuple[int, str]:
    if not script.exists():
        return 1, f"missing script: {script}"
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


async def grade_task(
    task: Task, kubeconfig: Path, cluster_name: str
) -> dict:
    env = {
        **os.environ,
        "KUBECONFIG": str(kubeconfig),
        "CLUSTER_NAME": cluster_name,
        "TASK_DIR": str(task.dir),
    }
    checks_meta = _load_checks(task)
    scaled = _scale_weights(
        [c["weight"] for c in checks_meta], task.weight
    )
    check_results = []
    earned = 0
    outputs = []
    for meta, points in zip(checks_meta, scaled, strict=True):
        code, out = await _run_script(meta["script"], env, task.dir)
        passed = code == 0
        got = points if passed else 0
        earned += got
        outputs.append(out)
        check_results.append(
            {
                "id": meta["id"],
                "description": meta["description"],
                "weight": points,
                "passed": passed,
                "earned": got,
                "output": out[-2000:],
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
    tasks: list[Task], kubeconfig: Path, cluster_name: str
) -> dict:
    results = []
    earned = 0
    domain_earned: dict[str, int] = defaultdict(int)
    domain_possible: dict[str, int] = defaultdict(int)

    for task in tasks:
        domain_possible[task.domain] += task.weight
        result = await grade_task(task, kubeconfig, cluster_name)
        earned += result["earned"]
        domain_earned[task.domain] += result["earned"]
        results.append(result)

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
        "results": results,
        "domains": domains,
    }
