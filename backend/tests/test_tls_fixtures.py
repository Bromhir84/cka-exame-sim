"""TLS exam questions ship a certificate and key the candidate can use."""

from __future__ import annotations

import asyncio
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.grader import _run_script  # noqa: E402

TASK = Path(__file__).resolve().parents[2] / "tasks" / "86-gateway-tls"


class GatewayTlsFixtureTests(unittest.TestCase):
    def test_cert_matches_key_for_the_exam_hostname(self) -> None:
        cert = TASK / "tls.crt"
        key = TASK / "tls.key"
        self.assertTrue(cert.is_file())
        self.assertTrue(key.is_file())
        subject = subprocess.check_output(
            ["openssl", "x509", "-in", str(cert), "-noout", "-subject", "-ext", "subjectAltName"],
            text=True,
        )
        self.assertIn("tls.cka.local", subject)
        cert_mod = subprocess.check_output(
            ["openssl", "x509", "-noout", "-modulus", "-in", str(cert)]
        )
        key_mod = subprocess.check_output(
            ["openssl", "rsa", "-noout", "-modulus", "-in", str(key)]
        )
        self.assertEqual(cert_mod, key_mod)

    def test_setup_copies_cert_and_key_into_the_candidate_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            bin_dir = Path(tmp) / "bin"
            home.mkdir()
            bin_dir.mkdir()
            kubectl = bin_dir / "kubectl"
            kubectl.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            kubectl.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
            env["KUBECONFIG"] = str(home / "kubeconfig-86-gateway-tls")
            env["TASK_DIR"] = str(TASK)
            # Same path the exam uses: the script is copied out of the task dir first.
            code, out = asyncio.run(_run_script(TASK / "setup.sh", env, TASK, timeout=30))
            self.assertEqual(code, 0, out)
            self.assertEqual((home / "tls.crt").read_bytes(), (TASK / "tls.crt").read_bytes())
            self.assertEqual((home / "tls.key").read_bytes(), (TASK / "tls.key").read_bytes())

    def test_setup_copies_into_the_cluster_home_not_beside_kubeconfig(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kube_dir = root / "kube"
            candidate = root / "candidate"
            bin_dir = root / "bin"
            kube_dir.mkdir()
            bin_dir.mkdir()
            kubectl = bin_dir / "kubectl"
            kubectl.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            kubectl.chmod(0o755)
            env = os.environ.copy()
            env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
            env["KUBECONFIG"] = str(kube_dir / "config")
            env["CANDIDATE_HOME"] = str(candidate)
            env["HOME"] = str(root / "ambient-home")
            env["TASK_DIR"] = str(TASK)
            code, out = asyncio.run(_run_script(TASK / "setup.sh", env, TASK, timeout=30))
            self.assertEqual(code, 0, out)
            self.assertEqual((candidate / "tls.crt").read_bytes(), (TASK / "tls.crt").read_bytes())
            self.assertEqual((candidate / "tls.key").read_bytes(), (TASK / "tls.key").read_bytes())
            self.assertFalse((kube_dir / "tls.crt").exists())
            self.assertFalse((root / "ambient-home" / "tls.crt").exists())


if __name__ == "__main__":
    unittest.main()
