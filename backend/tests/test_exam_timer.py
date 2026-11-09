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
    set_screen_lock_hold,
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

    def test_screen_lock_gives_the_wait_back(self) -> None:
        session = _session()
        deadline = session.ends_at
        assert deadline is not None
        set_screen_lock_hold(session, True)
        self.assertTrue(session_public(session)["timer_paused"])
        session.timer_paused_at = datetime.now(timezone.utc) - timedelta(seconds=15)
        set_screen_lock_hold(session, False, extend_seconds=15)
        assert session.ends_at is not None
        added = (session.ends_at - deadline).total_seconds()
        self.assertGreaterEqual(added, 14)
        self.assertLess(added, 20)
        self.assertFalse(session_public(session)["timer_paused"])

    def test_missed_lock_request_still_credits_the_gap(self) -> None:
        session = _session()
        deadline = session.ends_at
        assert deadline is not None
        set_screen_lock_hold(session, False, extend_seconds=30)
        assert session.ends_at is not None
        self.assertAlmostEqual((session.ends_at - deadline).total_seconds(), 30, delta=0.1)

    def test_lock_credit_is_capped(self) -> None:
        session = _session()
        deadline = session.ends_at
        assert deadline is not None
        set_screen_lock_hold(session, False, extend_seconds=100 * 3600)
        assert session.ends_at is not None
        self.assertEqual((session.ends_at - deadline).total_seconds(), 12 * 3600)

    def test_unlock_during_a_question_switch_stays_paused(self) -> None:
        session = _session(status=SessionStatus.SWITCHING)
        _pause_exam_timer(session)
        set_screen_lock_hold(session, True)
        set_screen_lock_hold(session, False, extend_seconds=50)
        self.assertIn("switching", session.timer_pause_reasons)
        self.assertNotIn("hidden", session.timer_pause_reasons)
        self.assertIsNotNone(session.timer_paused_at)
        self.assertTrue(session_public(session)["timer_paused"])

    def test_grading_ignores_a_screen_lock(self) -> None:
        session = _session(status=SessionStatus.GRADING)
        deadline = session.ends_at
        set_screen_lock_hold(session, True)
        set_screen_lock_hold(session, False, extend_seconds=40)
        self.assertEqual(session.ends_at, deadline)
        self.assertFalse(session.timer_pause_reasons)

    def test_ready_and_grading_keep_the_clock_running(self) -> None:
        for status in (SessionStatus.READY, SessionStatus.GRADING):
            session = _session(status=status)
            public = session_public(session)
            self.assertFalse(public["timer_paused"], status)
            self.assertIsNotNone(public["remaining_seconds"])


if __name__ == "__main__":
    unittest.main()
