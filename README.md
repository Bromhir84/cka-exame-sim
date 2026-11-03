# CKA Web Exam Simulator (MVP)

Browser-based CKA practice exam with a real Kubernetes cluster (kind), embedded terminal, 120-minute timer, and weighted auto-grading aligned to official CKA domains.

## Domains & weights

| Domain | Weight |
|--------|--------|
| Cluster Architecture, Installation & Configuration | 25% |
| Workloads & Scheduling | 15% |
| Services & Networking | 20% |
| Storage | 10% |
| Troubleshooting | 30% |

Pass hint: **66%** (same as the real exam).

Each **full exam** randomly draws **8 questions** from a **32-question bank**, filling fixed domain slots so the weights above always apply (no repeats within a run).

You can also choose a **single domain** in the lobby to practice every question in that domain (weights equalized to 100%).

## Prerequisites

- Docker Engine or Docker Desktop
- ~8 GB free RAM (kind cluster + Calico + ingress)

## Quick start

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine) running, and `git` on PATH.

### One-command install (clone + start)

**Windows (PowerShell):**

```powershell
git clone https://github.com/Bromhir84/cka-exame-sim.git; Set-Location cka-exame-sim; .\install.bat
```

**macOS / Linux:**

```bash
git clone https://github.com/Bromhir84/cka-exame-sim.git && cd cka-exame-sim && docker compose up --build -d && open http://localhost:5173 2>/dev/null || xdg-open http://localhost:5173 2>/dev/null || true
```

### Already cloned

**Windows:** double-click `install.bat`, or:

```bat
install.bat
```

**Any OS:**

```bash
docker compose up --build -d
```

- UI: http://localhost:5173
- API: http://localhost:8000

Click **Start Exam**, wait for the cluster to become ready (often **2–5 minutes** on first run while kind pulls node images and installs Calico + ingress), then work in the terminal. Click **End Exam** (or wait for the timer) for your score.

The exam workspace includes:

- **Terminal** — interactive bash with `kubectl` (and `k` alias) plus **Tab completion**
- **Docs** — allowlisted browser for exam-style resources only (`kubernetes.io` docs/blog and `github.com/kubernetes*`)

Only one exam session can run at a time. Ending the exam tears down the kind cluster.

## Development (without Compose UI)

```bash
# Backend (needs Docker socket + kind/kubectl on PATH, or use the backend container)
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

Validate the task bank locally:

```bash
python scripts/validate-tasks.py
```

## Project layout

- `backend/` — FastAPI session API, WebSocket PTY, grader
- `frontend/` — React + Vite + xterm.js exam UI
- `tasks/` — 32-task bank + `catalog.yaml` slots for domain-balanced draws
- `install.bat` — Windows one-click start
