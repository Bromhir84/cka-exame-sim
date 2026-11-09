"""Failed checks should name a typo, the wrong namespace, or a neighboring field."""

from __future__ import annotations

import asyncio
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.grader import explain_check_failure, grade_task  # noqa: E402
from app.mistake import (  # noqa: E402
    augment_failure,
    describe_typo,
    kinds_to_inspect,
    kubectl_calls,
    parse_object_rows,
)
from app.tasks_loader import Task  # noqa: E402


SECRET_MISSING = 'Error from server (NotFound): secrets "web-tls" not found\n'
SECRET_TRACE = "++ kubectl -n net-tls86 get secret web-tls -o jsonpath='{.type}'\n"


class TypoTests(unittest.TestCase):
    def test_names_a_single_character_slip(self):
        self.assertIn("extra `s` at the end", describe_typo("web-tlss", "web-tls"))
        self.assertIn("missing `-`", describe_typo("webtls", "web-tls"))
        self.assertIn(
            "has `5` where `nginx:1.27` has `7`",
            describe_typo("nginx:1.25", "nginx:1.27"),
        )
        self.assertIn("swaps `s` and `l`", describe_typo("web-tsl", "web-tls"))

    def test_names_case_and_separator_mistakes(self):
        self.assertIn("capitalization", describe_typo("Web-tls", "web-tls"))
        self.assertIn("uses `_`", describe_typo("web_tls", "web-tls"))

    def test_leaves_unrelated_values_alone(self):
        self.assertIsNone(describe_typo("production", "development"))
        self.assertIsNone(describe_typo("3", "1"))
        self.assertIsNone(describe_typo("web", "job"))
        self.assertIsNone(describe_typo("", "web-tls"))

    def test_comparison_adds_the_typo_sentence(self):
        text = explain_check_failure("", "++ '[' production = development ']'\n")
        self.assertNotIn("Likely mistake", text)
        self.assertIn("development", text)

    def test_grep_points_at_a_near_miss_in_the_object(self):
        trace = """\
++ echo '{"resources": ["pod"]}'
++ grep -q '"pods"'
"""
        text = explain_check_failure("", trace)
        self.assertIn("Likely mistake:", text)
        self.assertIn("missing `s` at the end", text)


class ClusterLookupTests(unittest.TestCase):
    def test_object_in_another_namespace(self):
        text = augment_failure(
            SECRET_MISSING.strip(),
            SECRET_MISSING,
            SECRET_TRACE,
            {"secret": [("default", "web-tls"), ("kube-system", "bootstrap")]},
        )
        self.assertIn(
            "Secret `web-tls` is in namespace `default`, not `net-tls86`",
            text,
        )

    def test_typo_in_the_expected_namespace(self):
        text = augment_failure(
            SECRET_MISSING.strip(),
            SECRET_MISSING,
            SECRET_TRACE,
            {"secret": [("net-tls86", "web-tlss"), ("default", "unrelated")]},
        )
        self.assertIn("extra `s` at the end", text)
        self.assertIn("namespace `net-tls86`", text)

    def test_mistyped_namespace_still_holds_the_object(self):
        output = 'Error from server (NotFound): namespaces "net-tls86" not found\n'
        trace = "++ kubectl -n net-tls86 get secret web-tls\n"
        text = augment_failure(
            output.strip(),
            output,
            trace,
            {
                "namespace": [("", "default"), ("", "net-tls8")],
                "secret": [("net-tls8", "web-tls")],
            },
        )
        self.assertIn("Secret `web-tls` is in namespace `net-tls8`", text)
        self.assertIn("not `net-tls86`", text)
        self.assertIn("missing `6` at the end", text)

    def test_namespace_typo_when_the_object_was_not_created(self):
        output = 'Error from server (NotFound): namespaces "net-tls86" not found\n'
        trace = "++ kubectl -n net-tls86 get secret web-tls\n"
        text = augment_failure(
            output.strip(),
            output,
            trace,
            {
                "namespace": [("", "default"), ("", "net-tls8")],
                "secret": [],
            },
        )
        self.assertIn("Namespace `net-tls8`", text)
        self.assertIn("missing `6` at the end", text)

    def test_reports_when_nothing_close_exists(self):
        text = augment_failure(
            SECRET_MISSING.strip(),
            SECRET_MISSING,
            SECRET_TRACE,
            {"secret": [("net-tls86", "other-secret")]},
        )
        self.assertIn("No Secret named `web-tls`", text)

    def test_failed_lookup_does_not_invent_an_absence(self):
        text = augment_failure(
            SECRET_MISSING.strip(),
            SECRET_MISSING,
            SECRET_TRACE,
            {"secret": None},
        )
        self.assertNotIn("Likely mistake", text)

    def test_value_stored_on_a_neighboring_field(self):
        text = augment_failure(
            "Expected `web`, but the cluster had `(empty)`.",
            "",
            "++ '[' '' = web ']'\n",
            {},
            {"spec": {"selector": {"application": "web"}}},
            "{.spec.selector.app}",
        )
        self.assertIn("`web` is set on `spec.selector.application`", text)
        self.assertIn("not `spec.selector.app`", text)

    def test_close_key_on_the_object(self):
        text = augment_failure(
            "Expected a value, but the cluster had `(empty)`.",
            "",
            "",
            {},
            {"data": {"app-conf": "hello"}},
            r"{.data.app\.conf}",
        )
        self.assertIn("`data.app-conf` is there instead", text)
        self.assertIn("has `-` where `app.conf` has `.`", text)

    def test_kinds_include_the_missing_namespace_and_the_object(self):
        output = 'Error from server (NotFound): namespaces "net-tls86" not found\n'
        trace = "++ kubectl -n net-tls86 get gateway web-gw\n"
        self.assertEqual(kinds_to_inspect(output, trace), ["namespace", "gateway"])

    def test_kubectl_trace_keeps_kind_name_namespace_and_jsonpath(self):
        trace = (
            "++ kubectl -n net-tls86 get secret web-tls -o jsonpath='{.type}'\n"
            "++ kubectl -n wl rollout status deploy/web --timeout=120s\n"
            "++ kubectl -n wl wait --for=condition=Ready pod/quiet --timeout=90s\n"
        )
        calls = kubectl_calls(trace)
        self.assertEqual(calls[0].namespace, "net-tls86")
        self.assertEqual(calls[0].kind, "secret")
        self.assertEqual(calls[0].name, "web-tls")
        self.assertEqual(calls[0].jsonpath, "{.type}")
        self.assertEqual((calls[1].kind, calls[1].name), ("deploy", "web"))
        self.assertEqual((calls[2].kind, calls[2].name), ("pod", "quiet"))

    def test_object_rows_skip_warnings(self):
        rows = parse_object_rows(
            "Warning: a plugin said hello\n"
            "default\tweb-tls\n"
            "\tunnamespaced\n"
        )
        self.assertEqual(rows, [("default", "web-tls"), ("", "unnamespaced")])


class GradeWiringTests(unittest.TestCase):
    def test_grade_task_reports_a_secret_left_in_the_wrong_namespace(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            checks = root / "checks"
            checks.mkdir()
            (checks / "secret.sh").write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "kubectl() {\n"
                "  echo 'Error from server (NotFound): secrets \"web-tls\" not found'\n"
                "  return 1\n"
                "}\n"
                "kubectl -n net-tls86 get secret web-tls\n",
                encoding="utf-8",
            )
            (root / "assessment.yaml").write_text(
                "checks:\n"
                "  - id: secret\n"
                "    description: TLS secret exists\n"
                "    weight: 100\n"
                "    script: checks/secret.sh\n",
                encoding="utf-8",
            )
            task = Task(
                id="sample",
                title="TLS secret",
                domain="networking",
                weight=4,
                prompt="create it",
                dir=root,
            )

            async def fake_list(_kind, _env, _cwd):
                return [("default", "web-tls")]

            with patch("app.grader._list_objects", fake_list):
                result = asyncio.run(
                    grade_task(task, Path("/tmp/missing-kubeconfig"), "unused")
                )
        failure = result["checks"][0]["failure"]
        self.assertIn("namespace `default`", failure)
        self.assertIn("not `net-tls86`", failure)
        self.assertFalse(result["checks"][0]["passed"])
