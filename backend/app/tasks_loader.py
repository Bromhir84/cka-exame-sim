from __future__ import annotations

import random
from collections import Counter, defaultdict
from copy import copy
from dataclasses import dataclass
from pathlib import Path
import yaml

from .config import TASKS_DIR

DOMAIN_LABELS = {
    "architecture": "Cluster Architecture, Installation & Configuration",
    "workloads": "Workloads & Scheduling",
    "networking": "Services & Networking",
    "storage": "Storage",
    "troubleshooting": "Troubleshooting",
}


@dataclass
class Slot:
    domain: str
    weight: int


@dataclass
class Task:
    id: str
    title: str
    domain: str
    weight: int
    prompt: str
    dir: Path

    @property
    def domain_label(self) -> str:
        return DOMAIN_LABELS.get(self.domain, self.domain)

    def to_public_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "domain": self.domain,
            "domain_label": self.domain_label,
            "weight": self.weight,
            "prompt": self.prompt,
        }


def _read_catalog(tasks_dir: Path) -> dict:
    catalog_path = tasks_dir / "catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"Task catalog not found: {catalog_path}")
    with catalog_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_slots(tasks_dir: Path | None = None) -> list[Slot]:
    root = tasks_dir or TASKS_DIR
    catalog = _read_catalog(root)
    raw = catalog.get("slots") or []
    if not raw:
        raise ValueError("catalog.yaml must define slots")
    slots = [Slot(domain=s["domain"], weight=int(s["weight"])) for s in raw]
    total = sum(s.weight for s in slots)
    if total != 100:
        raise ValueError(f"Slot weights must sum to 100, got {total}")
    for s in slots:
        if s.domain not in DOMAIN_LABELS:
            raise ValueError(f"Unknown slot domain: {s.domain}")
    return slots


def _load_task_dir(task_id: str, root: Path) -> Task:
    task_dir = root / task_id
    meta_path = task_dir / "task.yaml"
    prompt_path = task_dir / "prompt.md"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing {meta_path}")
    with meta_path.open(encoding="utf-8") as f:
        meta = yaml.safe_load(f) or {}
    domain = meta["domain"]
    if domain not in DOMAIN_LABELS:
        raise ValueError(f"Task {task_id} has unknown domain: {domain}")
    prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
    # Weight in YAML is ignored for exams; slots assign weight at selection time.
    weight = int(meta.get("weight") or 0)
    return Task(
        id=meta.get("id", task_id),
        title=meta["title"],
        domain=domain,
        weight=weight,
        prompt=prompt,
        dir=task_dir,
    )


def load_bank(tasks_dir: Path | None = None) -> list[Task]:
    root = tasks_dir or TASKS_DIR
    catalog = _read_catalog(root)
    task_ids: list[str] = catalog.get("bank") or catalog.get("tasks") or []
    if not task_ids:
        raise ValueError("catalog.yaml must define a bank of tasks")
    tasks = [_load_task_dir(tid, root) for tid in task_ids]
    ids = [t.id for t in tasks]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate task ids in bank")
    return tasks


def validate_catalog(tasks_dir: Path | None = None) -> None:
    root = tasks_dir or TASKS_DIR
    slots = load_slots(root)
    bank = load_bank(root)
    pools: dict[str, int] = Counter(t.domain for t in bank)
    needed: dict[str, int] = Counter(s.domain for s in slots)
    for domain, count in needed.items():
        have = pools.get(domain, 0)
        if have < count:
            raise ValueError(
                f"Domain {domain}: need at least {count} bank tasks for slots, have {have}"
            )
    for t in bank:
        for name in ("setup.sh", "grade.sh", "prompt.md", "task.yaml"):
            if not (t.dir / name).exists():
                raise FileNotFoundError(f"Missing {t.dir / name}")


def bank_summary(tasks_dir: Path | None = None) -> dict:
    root = tasks_dir or TASKS_DIR
    slots = load_slots(root)
    bank = load_bank(root)
    by_domain: dict[str, dict] = {}
    pools: dict[str, list[Task]] = defaultdict(list)
    for t in bank:
        pools[t.domain].append(t)
    for domain, label in DOMAIN_LABELS.items():
        tasks = pools.get(domain, [])
        by_domain[domain] = {
            "domain": domain,
            "label": label,
            "count": len(tasks),
            "titles": [t.title for t in tasks],
        }
    return {
        "count": len(bank),
        "slots": len(slots),
        "slot_weight_total": sum(s.weight for s in slots),
        "by_domain": list(by_domain.values()),
        "note": (
            f"{len(bank)}-question bank · {len(slots)} drawn per exam · "
            "official domain weights preserved"
        ),
    }


def select_exam_tasks(
    tasks_dir: Path | None = None,
    rng: random.Random | None = None,
) -> list[Task]:
    """Pick one unused bank task per slot; assign slot weight."""
    root = tasks_dir or TASKS_DIR
    slots = load_slots(root)
    bank = load_bank(root)
    rng = rng or random.Random()

    pools: dict[str, list[Task]] = defaultdict(list)
    for t in bank:
        pools[t.domain].append(t)
    for domain in pools:
        rng.shuffle(pools[domain])

    used: set[str] = set()
    selected: list[Task] = []
    for slot in slots:
        pool = [t for t in pools[slot.domain] if t.id not in used]
        if not pool:
            raise RuntimeError(
                f"No remaining bank tasks for domain {slot.domain}"
            )
        base = pool[0]
        used.add(base.id)
        task = copy(base)
        task.weight = slot.weight
        selected.append(task)
    return selected


# Back-compat alias used nowhere critical after migration
def load_tasks(tasks_dir: Path | None = None) -> list[Task]:
    return select_exam_tasks(tasks_dir)
