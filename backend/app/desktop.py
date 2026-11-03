from __future__ import annotations

import asyncio
import os
import re
import socket
from pathlib import Path

DESKTOP_IMAGE = os.getenv("DESKTOP_IMAGE", "cka-exame-sim-desktop")
DESKTOP_CONTEXT = os.getenv("DESKTOP_CONTEXT", "/app/desktop")


async def _run(cmd: list[str], timeout: int = 120) -> tuple[int, str]:
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    try:
        out, _ = await asyncio.wait_for(proc.communicate(), timeout=timeout)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.communicate()
        return 1, f"timed out: {' '.join(cmd)}"
    return proc.returncode or 0, (out or b"").decode("utf-8", errors="replace")


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 0))
        return int(s.getsockname()[1])


async def ensure_desktop_image() -> bool:
    code, _ = await _run(["docker", "image", "inspect", DESKTOP_IMAGE], timeout=30)
    if code == 0:
        return True
    ctx = Path(DESKTOP_CONTEXT)
    if not ctx.is_dir():
        return False
    code, _ = await _run(
        ["docker", "build", "-t", DESKTOP_IMAGE, str(ctx)],
        timeout=900,
    )
    return code == 0


async def start_desktop(
    session_id: str, kubeconfig: Path, cluster_name: str
) -> str | None:
    """Start a per-session noVNC desktop. Returns browser URL or None."""
    if not await ensure_desktop_image():
        return None

    name = f"cka-desk-{session_id}"
    await _run(["docker", "rm", "-f", name], timeout=60)

    host_port = _free_port()
    code, out = await _run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            name,
            "--hostname",
            f"desk-{session_id}",
            "-e",
            f"CLUSTER_NAME={cluster_name}",
            "-e",
            "VNC_PW=cka",
            "-p",
            f"{host_port}:6080",
            DESKTOP_IMAGE,
        ],
        timeout=120,
    )
    if code != 0:
        return None

    # Join kind bridge so control-plane DNS resolves
    await _run(["docker", "network", "connect", "kind", name], timeout=30)

    # Inject kubeconfig pointed at kind control-plane (docker-from-docker safe)
    try:
        text = kubeconfig.read_text(encoding="utf-8")
        cp = f"{cluster_name}-control-plane"
        text = re.sub(
            r"server:\s*https://[^\s]+",
            f"server: https://{cp}:6443",
            text,
            count=1,
        )
        patched = Path(f"/tmp/kubeconfig-desk-{session_id}")
        patched.write_text(text, encoding="utf-8")
        await _run(
            ["docker", "cp", str(patched), f"{name}:/home/candidate/.kube/config"],
            timeout=30,
        )
        await _run(
            [
                "docker",
                "exec",
                "-u",
                "root",
                name,
                "chown",
                "candidate:candidate",
                "/home/candidate/.kube/config",
            ],
            timeout=30,
        )
    except Exception:  # noqa: BLE001
        pass

    await asyncio.sleep(2)
    # Verify container still running
    code, _ = await _run(
        ["docker", "inspect", "-f", "{{.State.Running}}", name], timeout=15
    )
    if code != 0:
        return None

    return f"http://localhost:{host_port}/vnc.html?autoconnect=1&resize=scale"


async def stop_desktop(session_id: str) -> None:
    await _run(["docker", "rm", "-f", f"cka-desk-{session_id}"], timeout=60)
