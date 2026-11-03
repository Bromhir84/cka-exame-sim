#!/usr/bin/env python3
"""Validate task catalog weights and required files without a cluster."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.tasks_loader import load_tasks  # noqa: E402


def main() -> int:
    tasks = load_tasks(ROOT / "tasks")
    total = sum(t.weight for t in tasks)
    print(f"Loaded {len(tasks)} tasks, total weight={total}")
    for t in tasks:
        setup = t.dir / "setup.sh"
        grade = t.dir / "grade.sh"
        prompt = t.dir / "prompt.md"
        for p in (setup, grade, prompt):
            if not p.exists():
                print(f"MISSING {p}")
                return 1
        print(f"  OK {t.id:24} {t.weight:3}%  {t.domain}")
    if total != 100:
        print("FAIL: weights must sum to 100")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
