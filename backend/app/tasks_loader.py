from __future__ import annotations

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


def load_tasks(tasks_dir: Path | None = None) -> list[Task]:
    root = tasks_dir or TASKS_DIR
    catalog_path = root / "catalog.yaml"
    if not catalog_path.exists():
        raise FileNotFoundError(f"Task catalog not found: {catalog_path}")

    with catalog_path.open(encoding="utf-8") as f:
        catalog = yaml.safe_load(f) or {}

    task_ids: list[str] = catalog.get("tasks") or []
    tasks: list[Task] = []
    total_weight = 0

    for task_id in task_ids:
        task_dir = root / task_id
        meta_path = task_dir / "task.yaml"
        prompt_path = task_dir / "prompt.md"
        if not meta_path.exists():
            raise FileNotFoundError(f"Missing {meta_path}")
        with meta_path.open(encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}
        prompt = prompt_path.read_text(encoding="utf-8") if prompt_path.exists() else ""
        weight = int(meta["weight"])
        total_weight += weight
        tasks.append(
            Task(
                id=meta.get("id", task_id),
                title=meta["title"],
                domain=meta["domain"],
                weight=weight,
                prompt=prompt,
                dir=task_dir,
            )
        )

    if total_weight != 100:
        raise ValueError(f"Task weights must sum to 100, got {total_weight}")
    return tasks
