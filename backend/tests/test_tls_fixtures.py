"""TLS exam questions ship a certificate and key the candidate can use."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

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
            subprocess.run(
                ["bash", str(TASK / "setup.sh")],
                check=True,
                env=env,
                cwd=TASK,
            )
            self.assertEqual((home / "tls.crt").read_bytes(), (TASK / "tls.crt").read_bytes())
            self.assertEqual((home / "tls.key").read_bytes(), (TASK / "tls.key").read_bytes())


if __name__ == "__main__":
    unittest.main()
