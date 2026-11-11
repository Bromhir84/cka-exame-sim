"""Finishing the last question grades the exam instead of reopening earlier ones."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.session import (  # noqa: E402
    ExamSession,
    SessionStatus,
    _next_prefetch_task_id,
    _next_unfinished_task_id,
)
from app.tasks_loader import Task  # noqa: E402


def _task(task_id: str) -> Task:
    return Task(
        id=task_id,
        title=task_id,
        domain="workloads",
        weight=1,
        prompt="",
        dir=Path("/tmp"),
    )


def _session(ids: list[str], finished: list[str] | None = None) -> ExamSession:
    now = datetime.now(timezone.utc)
    tasks = [_task(task_id) for task_id in ids]
    return ExamSession(
        id="finish-nav",
        status=SessionStatus.READY,
        cluster_name="c",
        workdir=Path("/tmp/cka-finish"),
        kubeconfig=Path("/tmp/cka-finish/kube"),
        created_at=now,
        ends_at=now + timedelta(hours=2),
        tasks=tasks,
        active_task_id=ids[-1],
        task_results={task_id: {"earned": 0} for task_id in finished or []},
    )


class FinishNavigationTests(unittest.TestCase):
    def test_next_question_stays_ahead_in_the_set(self) -> None:
        session = _session(["q1", "q2", "q3"])
        session.active_task_id = "q1"
        self.assertEqual(_next_unfinished_task_id(session, "q1"), "q2")

    def test_next_question_skips_one_that_is_already_finished(self) -> None:
        session = _session(["q1", "q2", "q3"], finished=["q2"])
        self.assertEqual(_next_unfinished_task_id(session, "q1"), "q3")

    def test_finishing_the_last_question_does_not_wrap_to_the_first(self) -> None:
        session = _session(["q1", "q2", "q3"], finished=["q3"])
        session.active_task_id = "q3"
        self.assertIsNone(_next_unfinished_task_id(session, "q3"))
        self.assertIsNone(_next_prefetch_task_id(session))

    def test_prefetch_does_not_warm_question_one_from_the_last_question(self) -> None:
        session = _session(["q1", "q2", "q3"])
        session.active_task_id = "q3"
        self.assertIsNone(_next_prefetch_task_id(session))

    def test_prefetch_warms_the_following_unopened_question(self) -> None:
        session = _session(["q1", "q2", "q3"])
        session.active_task_id = "q1"
        self.assertEqual(_next_prefetch_task_id(session), "q2")
