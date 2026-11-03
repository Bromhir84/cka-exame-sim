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
  echo "==> Updating existing clone at $TARGET"
  git -C "$TARGET" pull --ff-only || git -C "$TARGET" pull
else
  echo "==> Cloning into $TARGET"
  git clone "$REPO_URL" "$TARGET"
fi

cd "$TARGET"
echo "==> Building images (backend, frontend, exam desktop)…"
docker compose build
echo "==> Starting stack…"
docker compose up -d

echo
echo "Ready."
echo "  UI:  http://localhost:5173"
echo "  API: http://localhost:8000"
echo
echo "First Start Exam often takes 2–5 minutes (kind + optional desktop)."
echo "Stop with:  docker compose down"
echo
if command -v open >/dev/null 2>&1; then
  open "http://localhost:5173" || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "http://localhost:5173" || true
fi
