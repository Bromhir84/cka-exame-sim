"""The exam clock pauses only on the switching-question screen."""

from __future__ import annotations

import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.session import (  # noqa: E402
    ExamSession,
    SessionStatus,
    _pause_exam_timer,
    _resume_exam_timer,
    session_public,
)


def _session(**overrides) -> ExamSession:
    now = datetime.now(timezone.utc)
    session = ExamSession(
        id="timer-test",
        status=SessionStatus.READY,
        cluster_name="c",
        workdir=Path("/tmp/cka-timer"),
        kubeconfig=Path("/tmp/cka-timer/kube"),
        created_at=now,
        ends_at=now + timedelta(seconds=500),
    )
    for key, value in overrides.items():
        setattr(session, key, value)
    return session


class ExamTimerTests(unittest.TestCase):
    def test_first_cluster_setup_does_not_pause_the_clock(self) -> None:
        session = _session(status=SessionStatus.PROVISIONING, ends_at=None)
        public = session_public(session)
        self.assertFalse(public["timer_paused"])
        self.assertIsNone(public["remaining_seconds"])

    def test_switching_screen_freezes_the_remaining_time(self) -> None:
        session = _session(status=SessionStatus.SWITCHING)
        paused_at = datetime.now(timezone.utc) - timedelta(seconds=40)
        session.ends_at = paused_at + timedelta(seconds=500)
        session.timer_paused_at = paused_at
        public = session_public(session)
        self.assertTrue(public["timer_paused"])
        self.assertEqual(public["remaining_seconds"], 500)

    def test_resume_gives_back_the_wait(self) -> None:
        session = _session()
        deadline = session.ends_at
        assert deadline is not None
        session.timer_paused_at = datetime.now(timezone.utc) - timedelta(seconds=25)
        _resume_exam_timer(session)
        assert session.ends_at is not None
        added = (session.ends_at - deadline).total_seconds()
        self.assertGreaterEqual(added, 24)
        self.assertLess(added, 30)
        self.assertIsNone(session.timer_paused_at)

    def test_pause_does_not_move_the_original_stamp(self) -> None:
        session = _session()
        _pause_exam_timer(session)
        first = session.timer_paused_at
        _pause_exam_timer(session)
        self.assertEqual(session.timer_paused_at, first)

    def test_ready_and_grading_keep_the_clock_running(self) -> None:
        for status in (SessionStatus.READY, SessionStatus.GRADING):
            session = _session(status=status)
            public = session_public(session)
            self.assertFalse(public["timer_paused"], status)
            self.assertIsNotNone(public["remaining_seconds"])


if __name__ == "__main__":
    unittest.main()
