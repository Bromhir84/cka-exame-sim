#!/usr/bin/env python3
"""Validate task bank + exam slots without a cluster."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.tasks_loader import (  # noqa: E402
    bank_summary,
    select_exam_tasks,
    validate_catalog,
)


def main() -> int:
    tasks_dir = ROOT / "tasks"
    try:
        validate_catalog(tasks_dir)
    except Exception as exc:  # noqa: BLE001
        print(f"FAIL: {exc}")
        return 1

    summary = bank_summary(tasks_dir)
    print(summary["note"])
    for d in summary["by_domain"]:
        print(f"  {d['domain']:16} {d['count']:2} tasks")

    drawn = select_exam_tasks(tasks_dir)
    total = sum(t.weight for t in drawn)
    print(f"Sample draw ({len(drawn)} tasks, weight={total}):")
    for t in drawn:
        print(f"  {t.id:28} {t.weight:3}%  {t.domain}")
    if total != 100:
        print("FAIL: drawn weights must sum to 100")
        return 1
    if len({t.id for t in drawn}) != len(drawn):
        print("FAIL: duplicate task ids in draw")
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
