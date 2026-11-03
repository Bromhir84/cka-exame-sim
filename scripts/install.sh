#!/usr/bin/env bash
# One-line install: curl -fsSL .../install.sh | bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Bromhir84/cka-exame-sim.git}"
DIR_NAME="${DIR_NAME:-cka-exame-sim}"
TARGET="${TARGET_DIR:-$HOME/$DIR_NAME}"

echo "==> CKA Exam Simulator installer"
echo

if ! command -v git >/dev/null 2>&1; then
  echo "ERROR: git is required"
  exit 1
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "ERROR: Docker is required (Docker Desktop / Engine)"
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker is installed but not running"
  exit 1
fi

if [ -d "$TARGET/.git" ]; then
  echo "==> Checking for updates at $TARGET"
  branch="$(git -C "$TARGET" rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)"
  if git -C "$TARGET" fetch origin "$branch" >/dev/null 2>&1; then
    local_sha="$(git -C "$TARGET" rev-parse HEAD)"
    remote_sha="$(git -C "$TARGET" rev-parse "origin/$branch")"
    if [ "$local_sha" != "$remote_sha" ]; then
      echo "    Update available — pulling origin/$branch..."
      if git -C "$TARGET" pull --ff-only origin "$branch"; then
        echo "    Updated successfully."
      else
        echo "    [WARN] git pull failed; continuing with local copy."
      fi
    else
      echo "    Already up to date."
    fi
  else
    echo "    Could not reach origin — continuing with local copy."
  fi
else
  echo "==> Cloning into $TARGET"
  git clone "$REPO_URL" "$TARGET"
fi

cd "$TARGET"
echo "==> Building images (backend, frontend, exam desktop)…"
docker compose build
echo "==> Starting stack…"
docker compose up -d

echo "==> Waiting for UI + API (http://localhost:5173/api/health)…"
ready=0
for i in $(seq 1 90); do
  if curl -fsS "http://localhost:5173/api/health" >/dev/null 2>&1; then
    ready=1
    break
  fi
  sleep 2
done
if [ "$ready" -ne 1 ]; then
  echo "ERROR: Stack did not become healthy in time. Check: docker compose logs"
  exit 1
fi

echo
echo "Ready."
echo "  UI:  http://localhost:5173"
echo "  API: http://localhost:8000"
echo
echo "First Start Exam can take several minutes (kind + networking + optional desktop)."
echo "Stop with:  docker compose down"
echo
if command -v open >/dev/null 2>&1; then
  open "http://localhost:5173" || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:5173" || true
fi
