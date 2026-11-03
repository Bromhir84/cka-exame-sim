from __future__ import annotations

import asyncio
import fcntl
import os
import pty
import struct
import termios

from fastapi import WebSocket, WebSocketDisconnect

from .session import SessionStatus, get_session


def _set_winsize(fd: int, rows: int, cols: int) -> None:
    winsize = struct.pack("HHHH", rows, cols, 0, 0)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def _write_bashrc(path, cluster_name: str) -> None:
    path.write_text(
        "\n".join(
            [
                "# CKA exam practice shell",
                'export KUBECONFIG="$KUBECONFIG"',
                "export ETCDCTL_API=3",
                f"export CLUSTER_NAME={cluster_name}",
                "export TERM=xterm-256color",
                r"export PS1='candidate@cka:\w\$ '",
                "alias k=kubectl",
                "",
                "# bash completion + kubectl",
                "if [ -f /usr/share/bash-completion/bash_completion ]; then",
                "  . /usr/share/bash-completion/bash_completion",
                "elif [ -f /etc/bash_completion ]; then",
                "  . /etc/bash_completion",
                "fi",
                "if command -v kubectl >/dev/null 2>&1; then",
                "  source <(kubectl completion bash)",
                "  complete -o default -F __start_kubectl k",
                "fi",
                "",
                "echo 'CKA practice shell — kubectl + completion ready (Tab). Alias: k=kubectl'",
                "echo 'Docs browser: use the Docs tab (allowlisted kubernetes.io / GitHub only).'",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


async def terminal_websocket(websocket: WebSocket, session_id: str) -> None:
    session = get_session(session_id)
    if not session or session.status != SessionStatus.READY:
        await websocket.close(code=4404)
        return

    await websocket.accept()

    env = os.environ.copy()
    env["KUBECONFIG"] = str(session.kubeconfig)
    env["TERM"] = "xterm-256color"
    # Ensure interactive completion works
    env["BASH_ENV"] = ""

    bashrc = session.workdir / ".bashrc"
    _write_bashrc(bashrc, session.cluster_name)

    master_fd, slave_fd = pty.openpty()
    _set_winsize(slave_fd, 24, 80)

    # -i enables programmable completion / readline Tab behavior
    proc = await asyncio.create_subprocess_exec(
        "bash",
        "-i",
        "--rcfile",
        str(bashrc),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=str(session.workdir),
        env=env,
        start_new_session=True,
    )
    os.close(slave_fd)

    loop = asyncio.get_event_loop()
    stop = asyncio.Event()

    async def read_pty() -> None:
        try:
            while not stop.is_set():
                data = await loop.run_in_executor(None, os.read, master_fd, 4096)
                if not data:
                    break
                await websocket.send_bytes(data)
        except Exception:  # noqa: BLE001
            pass
        finally:
            stop.set()

    async def read_ws() -> None:
        try:
            while not stop.is_set():
                message = await websocket.receive()
                if message.get("type") == "websocket.disconnect":
                    break
                if "bytes" in message and message["bytes"] is not None:
                    payload = message["bytes"]
                    await loop.run_in_executor(None, os.write, master_fd, payload)
                elif "text" in message and message["text"] is not None:
                    text = message["text"]
                    if text.startswith("resize:"):
                        try:
                            _, dims = text.split(":", 1)
                            cols_s, rows_s = dims.split("x")
                            _set_winsize(master_fd, int(rows_s), int(cols_s))
                        except ValueError:
                            pass
                    else:
                        await loop.run_in_executor(
                            None, os.write, master_fd, text.encode("utf-8")
                        )
        except WebSocketDisconnect:
            pass
        except Exception:  # noqa: BLE001
            pass
        finally:
            stop.set()

    reader = asyncio.create_task(read_pty())
    writer = asyncio.create_task(read_ws())
    await stop.wait()
    reader.cancel()
    writer.cancel()
    try:
        proc.terminate()
        await asyncio.wait_for(proc.wait(), timeout=3)
    except Exception:  # noqa: BLE001
        try:
            proc.kill()
        except Exception:  # noqa: BLE001
            pass
    try:
        os.close(master_fd)
    except OSError:
        pass
    try:
        await websocket.close()
    except Exception:  # noqa: BLE001
        pass
