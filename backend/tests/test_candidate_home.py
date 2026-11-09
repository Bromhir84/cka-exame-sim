"""Each question cluster has its own terminal home directory."""

from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.grader import run_setup  # noqa: E402
from app.session import (  # noqa: E402
    ExamSession,
    SessionStatus,
    TaskClusterState,
    candidate_home,
    home_for,
    kubeconfig_for,
    prepare_candidate_home,
)
from app.tasks_loader import Task  # noqa: E402


class CandidateHomeTests(unittest.TestCase):
    def test_questions_do_not_share_a_home(self) -> None:
        workdir = Path("/tmp/cka-session")
        first = home_for(workdir, "01-rbac")
        second = home_for(workdir, "86-gateway-tls")
        self.assertEqual(first, workdir / "home" / "01-rbac")
        self.assertNotEqual(first, second)
        self.assertEqual(kubeconfig_for(workdir, "01-rbac"), first / ".kube" / "config")
        self.assertFalse(
            str(kubeconfig_for(workdir, "86-gateway-tls")).startswith(str(first))
        )

    def test_preparing_a_home_keeps_files_already_there(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = prepare_candidate_home(Path(tmp), "01-rbac")
            note = home / "answer.yaml"
            note.write_text("kept\n", encoding="utf-8")
            again = prepare_candidate_home(Path(tmp), "01-rbac")
            self.assertEqual(again, home)
            self.assertEqual(note.read_text(encoding="utf-8"), "kept\n")
            self.assertTrue((home / ".kube").is_dir())

    def test_terminal_home_follows_the_active_cluster(self) -> None:
        workdir = Path("/tmp/cka-homes")
        session = ExamSession(
            id="s",
            status=SessionStatus.READY,
            cluster_name="cka-s-00",
            workdir=workdir,
            kubeconfig=kubeconfig_for(workdir, "01-rbac"),
            created_at=datetime.now(timezone.utc),
            active_task_id="01-rbac",
        )
        session.task_clusters["01-rbac"] = TaskClusterState(
            cluster_name="cka-s-00",
            kubeconfig=kubeconfig_for(workdir, "01-rbac"),
            home=home_for(workdir, "01-rbac"),
        )
        session.task_clusters["86-gateway-tls"] = TaskClusterState(
            cluster_name="cka-s-01",
            kubeconfig=kubeconfig_for(workdir, "86-gateway-tls"),
            home=home_for(workdir, "86-gateway-tls"),
        )
        self.assertEqual(candidate_home(session), home_for(workdir, "01-rbac"))
        session.active_task_id = "86-gateway-tls"
        session.kubeconfig = kubeconfig_for(workdir, "86-gateway-tls")
        self.assertEqual(candidate_home(session), home_for(workdir, "86-gateway-tls"))
        self.assertNotEqual(candidate_home(session), workdir)

    def test_setup_receives_that_questions_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task_dir = root / "task"
            task_dir.mkdir()
            home = root / "home" / "q"
            (task_dir / "setup.sh").write_text(
                "#!/bin/bash\n"
                "set -euo pipefail\n"
                "printf '%s' \"$HOME\" > \"$TASK_DIR/seen-home\"\n"
                "printf '%s' \"$CANDIDATE_HOME\" > \"$TASK_DIR/seen-candidate\"\n",
                encoding="utf-8",
            )
            task = Task(
                id="q",
                title="Question",
                domain="networking",
                weight=1,
                prompt="do it",
                dir=task_dir,
            )
            asyncio.run(
                run_setup(task, root / "elsewhere" / "config", "cluster", home=home)
            )
            self.assertEqual((task_dir / "seen-home").read_text(encoding="utf-8"), str(home))
            self.assertEqual(
                (task_dir / "seen-candidate").read_text(encoding="utf-8"), str(home)
            )
