import os
from pathlib import Path

TASKS_DIR = Path(os.getenv("TASKS_DIR", "/app/tasks"))
SESSIONS_DIR = Path(os.getenv("SESSIONS_DIR", "/var/lib/cka-sessions"))
EXAM_DURATION_MINUTES = int(os.getenv("EXAM_DURATION_MINUTES", "120"))
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]
PASS_THRESHOLD = 66
KIND_IMAGE = os.getenv("KIND_IMAGE", "kindest/node:v1.31.4")
