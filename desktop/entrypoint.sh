#!/usr/bin/env bash
set -euo pipefail

export USER="${USER:-candidate}"
export HOME="${HOME:-/home/candidate}"
mkdir -p "$HOME/.vnc" "$HOME/.kube"

# VNC password
echo "${VNC_PW:-cka}" | vncpasswd -f > "$HOME/.vnc/passwd"
chmod 600 "$HOME/.vnc/passwd"

# Kill stale sessions
vncserver -kill :1 >/dev/null 2>&1 || true
rm -f /tmp/.X1-lock /tmp/.X11-unix/X1 || true

geometry="${VNC_RESOLUTION:-1280x800}"
vncserver :1 -geometry "$geometry" -depth 24 -localhost no

# noVNC
websockify --web=/usr/share/novnc/ 0.0.0.0:6080 localhost:5901 &
echo "Desktop ready — noVNC on :6080"
wait
