from __future__ import annotations

import asyncio
import logging
import os
import re
import socket
from dataclasses import dataclass
from pathlib import Path

import httpx
from fastapi import HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response

logger = logging.getLogger(__name__)

DESKTOP_IMAGE = os.getenv("DESKTOP_IMAGE", "cka-exame-sim-desktop")
DESKTOP_CONTEXT = os.getenv("DESKTOP_CONTEXT", "/app/desktop")


@dataclass
class DesktopRuntime:
    container: str
    last_error: str | None = None


_runtimes: dict[str, DesktopRuntime] = {}


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


async def ensure_desktop_image() -> tuple[bool, str]:
    code, _ = await _run(["docker", "image", "inspect", DESKTOP_IMAGE], timeout=30)
    if code == 0:
        return True, ""
    ctx = Path(DESKTOP_CONTEXT)
    if not ctx.is_dir():
        return False, f"desktop build context missing: {ctx}"
    logger.warning("Desktop image %s missing; building from %s", DESKTOP_IMAGE, ctx)
    code, out = await _run(
        ["docker", "build", "-t", DESKTOP_IMAGE, str(ctx)],
        timeout=900,
    )
    if code != 0:
        return False, f"desktop image build failed:\n{out[-2000:]}"
    return True, ""


async def _self_networks() -> list[str]:
    """Docker networks this backend container is attached to (compose + others)."""
    host = socket.gethostname()
    code, out = await _run(
        [
            "docker",
            "inspect",
            "-f",
            "{{range $k, $v := .NetworkSettings.Networks}}{{$k}}\n{{end}}",
            host,
        ],
        timeout=20,
    )
    if code != 0:
        # Fallback common compose project network name
        return ["cka-exame-sim_default"]
    nets = [line.strip() for line in out.splitlines() if line.strip()]
    return nets or ["cka-exame-sim_default"]


async def _connect_networks(container: str, networks: list[str]) -> None:
    for net in networks:
        code, out = await _run(
            ["docker", "network", "connect", net, container], timeout=30
        )
        # Already connected is fine
        if code != 0 and "already exists" not in out.lower() and "already connected" not in out.lower():
            logger.warning("network connect %s -> %s: %s", container, net, out[-300:])


def desktop_public_url(session_id: str) -> str:
    """Same-origin URL so the Docs/Desktop UI can iframe noVNC through nginx → backend."""
    base = f"/api/sessions/{session_id}/desktop"
    # noVNC `path` is relative to the page host (no leading slash works best)
    ws_path = f"api/sessions/{session_id}/desktop/websockify"
    return f"{base}/vnc.html?autoconnect=1&resize=scale&path={ws_path}"


def desktop_upstream_http(session_id: str) -> str:
    return f"http://cka-desk-{session_id}:6080"


def get_desktop_error(session_id: str) -> str | None:
    rt = _runtimes.get(session_id)
    return rt.last_error if rt else None


async def start_desktop(
    session_id: str, kubeconfig: Path, cluster_name: str
) -> str | None:
    """Start a per-session noVNC desktop. Returns same-origin browser URL or None."""
    ok, err = await ensure_desktop_image()
    if not ok:
        logger.error("Desktop unavailable: %s", err)
        _runtimes[session_id] = DesktopRuntime(
            container=f"cka-desk-{session_id}", last_error=err
        )
        return None

    name = f"cka-desk-{session_id}"
    await _run(["docker", "rm", "-f", name], timeout=60)

    # No host port publish: reach the container via the compose/backend network + HTTP proxy.
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
            DESKTOP_IMAGE,
        ],
        timeout=120,
    )
    if code != 0:
        msg = f"failed to start desktop container:\n{out[-1500:]}"
        logger.error(msg)
        _runtimes[session_id] = DesktopRuntime(container=name, last_error=msg)
        return None

    networks = await _self_networks()
    await _connect_networks(name, networks)
    # Kind network so kubectl inside the desktop can reach the control-plane
    await _connect_networks(name, ["kind"])

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
    except Exception as exc:  # noqa: BLE001
        logger.warning("desktop kubeconfig inject failed: %s", exc)

    # Wait until noVNC answers
    upstream = desktop_upstream_http(session_id)
    ready = False
    last = ""
    for _ in range(30):
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{upstream}/vnc.html")
                if resp.status_code < 500:
                    ready = True
                    break
                last = f"HTTP {resp.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = str(exc)
        await asyncio.sleep(1)

    if not ready:
        code, logs = await _run(["docker", "logs", "--tail", "80", name], timeout=30)
        msg = f"desktop did not become ready ({last}). logs:\n{logs[-1500:]}"
        logger.error(msg)
        await _run(["docker", "rm", "-f", name], timeout=60)
        _runtimes[session_id] = DesktopRuntime(container=name, last_error=msg)
        return None

    _runtimes[session_id] = DesktopRuntime(container=name, last_error=None)
    return desktop_public_url(session_id)


async def stop_desktop(session_id: str) -> None:
    await _run(["docker", "rm", "-f", f"cka-desk-{session_id}"], timeout=60)
    _runtimes.pop(session_id, None)


async def proxy_desktop_http(session_id: str, path: str, request: Request) -> Response:
    """Reverse-proxy noVNC static assets / HTTP to the session desktop container."""
    if session_id not in _runtimes and not path:
        raise HTTPException(status_code=404, detail="desktop not running")
    upstream = desktop_upstream_http(session_id)
    # Normalize path
    rel = path.lstrip("/") if path else ""
    url = f"{upstream}/{rel}" if rel else f"{upstream}/"
    if request.url.query:
        url = f"{url}?{request.url.query}"

    headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in {"host", "content-length"}
    }
    body = await request.body()
    try:
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=False) as client:
            upstream_resp = await client.request(
                request.method,
                url,
                content=body if body else None,
                headers=headers,
            )
    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=502, detail=f"desktop upstream unreachable: {exc}"
        ) from exc

    excluded = {"content-encoding", "transfer-encoding", "content-length", "connection"}
    out_headers = {
        k: v
        for k, v in upstream_resp.headers.items()
        if k.lower() not in excluded
    }
    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        headers=out_headers,
        media_type=upstream_resp.headers.get("content-type"),
    )


async def proxy_desktop_websockify(websocket: WebSocket, session_id: str) -> None:
    """Bridge browser ↔ websockify inside the desktop container."""
    await websocket.accept()
    upstream = desktop_upstream_http(session_id).replace("http://", "ws://") + "/"
    # websockify accepts WS on the same port as HTTP
    try:
        import websockets  # bundled with uvicorn[standard] / websockets dep
    except ImportError as exc:
        await websocket.close(code=1011)
        raise HTTPException(status_code=500, detail="websockets missing") from exc

    try:
        async with websockets.connect(
            upstream,
            subprotocols=websocket.scope.get("subprotocols") or None,
            open_timeout=10,
        ) as upstream_ws:

            async def client_to_upstream() -> None:
                try:
                    while True:
                        msg = await websocket.receive()
                        if msg["type"] == "websocket.disconnect":
                            break
                        if msg.get("bytes") is not None:
                            await upstream_ws.send(msg["bytes"])
                        elif msg.get("text") is not None:
                            await upstream_ws.send(msg["text"])
                except WebSocketDisconnect:
                    pass

            async def upstream_to_client() -> None:
                try:
                    async for message in upstream_ws:
                        if isinstance(message, bytes):
                            await websocket.send_bytes(message)
                        else:
                            await websocket.send_text(message)
                except Exception:  # noqa: BLE001
                    pass

            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(client_to_upstream()),
                    asyncio.create_task(upstream_to_client()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
    except Exception as exc:  # noqa: BLE001
        logger.warning("desktop websocket proxy failed: %s", exc)
        try:
            await websocket.close(code=1011)
        except Exception:  # noqa: BLE001
            pass
