"""Grade failures should name the value that was actually on the cluster."""

from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.grader import (  # noqa: E402
    _run_check,
    explain_check_failure,
    grade_task,
)
from app.tasks_loader import Task  # noqa: E402


class ExplainCheckFailureTests(unittest.TestCase):
    def test_comparison_names_expected_and_actual(self):
        trace = """\
+ source /tmp/check.sh
++ set -euo pipefail
+++ printf nginx:1.25
++ IMG=nginx:1.25
++ '[' nginx:1.25 = nginx:1.27 ']'
"""
        text = explain_check_failure("", trace)
        self.assertIn("Expected `nginx:1.27`", text)
        self.assertIn("`nginx:1.25` (IMG)", text)
        self.assertIn("has `5` where `nginx:1.27` has `7`", text)

    def test_grep_shows_the_object_that_was_missing_the_text(self):
        trace = """\
++ ROLE_JSON='{"resources": ["configmaps"]}'
++ echo '{"resources": ["configmaps"]}'
++ grep -q '"pods"'
"""
        text = explain_check_failure("", trace)
        self.assertIn("contain `\"pods\"`", text)
        self.assertIn("configmaps", text)
        self.assertNotIn("pods", text.split("What was on the cluster", 1)[-1].split("configmaps", 1)[0])

    def test_empty_value_is_called_out(self):
        trace = "++ EP=\n++ '[' -n '' ']'\n"
        text = explain_check_failure("", trace)
        self.assertIn("Expected a value", text)
        self.assertIn("(empty)", text)
        self.assertIn("EP", text)

    def test_value_that_should_have_been_cleared(self):
        trace = "++ BAD=ssd\n++ '[' -z ssd ']'\n"
        text = explain_check_failure("", trace)
        self.assertIn("Expected this to be empty", text)
        self.assertIn("`ssd` (BAD)", text)

    def test_kubernetes_not_found_is_the_reason(self):
        output = 'Error from server (NotFound): serviceaccounts "deployer" not found\n'
        trace = "++ kubectl -n rbac-lab get sa deployer\n"
        text = explain_check_failure(output, trace)
        self.assertIn("serviceaccounts", text)
        self.assertIn("deployer", text)
        self.assertIn("kubectl -n rbac-lab get sa deployer", text)

    def test_timeout_is_explicit(self):
        self.assertIn("timed out", explain_check_failure("script timed out", ""))


class LiveCheckTests(unittest.TestCase):
    def test_pipeline_grep_uses_the_echoed_object_even_when_traced_last(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "role.sh"
            script.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "ROLE_JSON='{\"resources\":[\"configmaps\"]}'\n"
                "echo \"$ROLE_JSON\" | grep -q '\"pods\"'\n",
                encoding="utf-8",
            )
            code, out, trace = asyncio.run(
                _run_check(script, {}, Path(tmp), timeout=10)
            )
        self.assertNotEqual(code, 0)
        text = explain_check_failure(out, trace)
        self.assertIn("pods", text)
        self.assertIn("configmaps", text)
        self.assertNotIn("stopped on: echo", text)

    def test_failed_image_check_reports_the_running_image(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "image.sh"
            script.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "IMG=$(printf 'nginx:1.25')\n"
                '[ "$IMG" = "nginx:1.27" ]\n',
                encoding="utf-8",
            )
            code, out, trace = asyncio.run(
                _run_check(script, {}, Path(tmp), timeout=10)
            )
        self.assertNotEqual(code, 0)
        text = explain_check_failure(out, trace)
        self.assertIn("nginx:1.27", text)
        self.assertIn("nginx:1.25", text)

    def test_grade_task_stores_the_failure_next_to_the_solution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checks = root / "checks"
            checks.mkdir()
            (checks / "image.sh").write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "IMG=$(printf 'nginx:1.25')\n"
                '[ "$IMG" = "nginx:1.27" ]\n',
                encoding="utf-8",
            )
            (root / "assessment.yaml").write_text(
                "checks:\n"
                "  - id: image\n"
                "    description: Image is nginx:1.27\n"
                "    weight: 100\n"
                "    script: checks/image.sh\n",
                encoding="utf-8",
            )
            (root / "answers.md").write_text("## Steps\nset the image\n", encoding="utf-8")
            task = Task(
                id="sample",
                title="Fix the image",
                domain="troubleshooting",
                weight=4,
                prompt="fix it",
                dir=root,
            )
            result = asyncio.run(grade_task(task, Path("/tmp/missing-kubeconfig"), "unused"))
        self.assertEqual(result["answers"], "## Steps\nset the image\n")
        self.assertFalse(result["checks"][0]["passed"])
        self.assertIn("nginx:1.25", result["checks"][0]["failure"])
        self.assertIn("nginx:1.27", result["checks"][0]["failure"])
        self.assertIn("has `5` where `nginx:1.27` has `7`", result["checks"][0]["failure"])
