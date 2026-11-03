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

Each **full exam** randomly draws **16 questions** from a **112-question bank**, filling fixed domain slots so the weights above always apply (no repeats within a run).

Each question runs on its **own kind cluster**. Use **Previous / Next** to move between questions — leaving a question parks its cluster (your work is preserved); returning reconnects. A question is provisioned the first time you open it. **Finish question** grades that item quietly, removes its cluster (frees RAM), and keeps the result hidden until **End Exam**, which grades any remaining open clusters and shows the full score report.

You can also choose a **single domain** in the lobby to practice every question in that domain (weights equalized to 100%).

## Prerequisites

- Docker Engine or Docker Desktop
- ~8 GB free RAM for the first question cluster; each additional opened question keeps another kind cluster (RAM adds up if you open many)

## Quick start

Requires [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine) running, and `git` on PATH.

### One-command install (clone/update + start)

**Windows (PowerShell):**

```powershell
irm https://raw.githubusercontent.com/Bromhir84/cka-exame-sim/main/scripts/install.ps1 | iex
```

**macOS / Linux:**

```bash
curl -fsSL https://raw.githubusercontent.com/Bromhir84/cka-exame-sim/main/scripts/install.sh | bash
```

Or clone manually:

```powershell
git clone https://github.com/Bromhir84/cka-exame-sim.git; Set-Location cka-exame-sim; .\install.bat
```

### Already cloned

**Windows:** double-click `install.bat`, or:

```bat
install.bat
```

On start, `install.bat` / the one-line installers `git fetch` and pull updates from GitHub when available (skipped quietly if offline).

**Any OS:**

```bash
docker compose up --build -d
```


- UI: http://localhost:5173
- API: http://localhost:8000

Click **Start Exam**, wait for the environment to become ready (kind cluster, Calico, ingress, optional desktop). The first run can take several minutes while images are pulled; later starts are usually faster. Then work in the terminal (or Desktop tab). Click **End Exam** (or wait for the timer) for your score.

The exam workspace includes:

- **Terminal** — interactive bash with `kubectl` (and `k` alias) plus **Tab completion**
- **Docs** — allowlisted browser for exam-style resources only (`kubernetes.io` docs/blog and `github.com/kubernetes*`)
- **Desktop** — optional noVNC remote desktop (XFCE + allowlisted Firefox) for exam-style realism

Grading uses multi-step checks with partial credit; after you end the exam, solutions (`answers.md`) appear in the score report.

Only one exam session can run at a time. Ending the exam tears down all question clusters and the desktop container.

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

- `backend/` — FastAPI session API, WebSocket PTY, grader, desktop lifecycle
- `frontend/` — React + Vite + xterm.js exam UI
- `desktop/` — XFCE + TigerVNC + noVNC + kubectl + allowlisted Firefox image
- `tasks/` — 56-task bank + `catalog.yaml` slots for domain-balanced draws
- `scripts/install.sh` / `scripts/install.ps1` — one-line installers
- `install.bat` — Windows one-click start

## License / attribution

This project is independent practice software. Remote-desktop exam UX ideas were inspired by public descriptions of [CK-X](https://github.com/sailor-sh/CK-X); **no CK-X source code is vendored** (CK-X is BSL-licensed).
