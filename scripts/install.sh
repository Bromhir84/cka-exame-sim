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
  echo "==> Updating $TARGET to origin/main"
  if ! git -C "$TARGET" fetch origin main; then
    echo "ERROR: Could not fetch origin/main. Refusing to start an older copy."
    exit 1
  fi
  # The install directory is the running app. Local edits must not keep the old UI.
  echo "    Checking out origin/main. Local changes in this folder are replaced."
  git -C "$TARGET" checkout -f -B main origin/main
else
  echo "==> Cloning into $TARGET"
  git clone "$REPO_URL" "$TARGET"
fi

cd "$TARGET"
export GIT_SHA="$(git rev-parse HEAD)"
echo "==> Building version ${GIT_SHA:0:7}"
echo "    Rebuilding the UI image so the exam clock fix is the one that runs."
docker compose build --no-cache frontend
docker compose build backend
echo "==> Starting stack…"
docker compose up -d --force-recreate

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

echo "==> Pulling cluster images (reused by every kind cluster)…"
if ! docker compose exec -T backend python -m app.preload_images; then
  echo "ERROR: Failed to pull cluster images. Check: docker compose logs backend"
  exit 1
fi

echo
SHORT_SHA="${GIT_SHA:0:7}"
echo "Ready (build ${SHORT_SHA})."
echo "  UI:  http://localhost:5173"
echo "  API: http://localhost:8000"
echo
echo "Reload the exam page if it was already open. The header should say build ${SHORT_SHA}."
echo "Cluster images are cached. New clusters load them instead of downloading again."
echo "The first cluster still takes a few minutes to boot."
echo "Stop with:  docker compose down"
echo
UI_URL="http://localhost:5173/?v=${SHORT_SHA}"
if command -v open >/dev/null 2>&1; then
  open "$UI_URL" || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$UI_URL" || true
fi
