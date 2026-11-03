from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS, SESSIONS_DIR
from .session import (
    create_session,
    destroy_session,
    end_session,
    get_session,
    session_public,
)
from .tasks_loader import bank_summary, validate_catalog
from .terminal import terminal_websocket


@asynccontextmanager
async def lifespan(_app: FastAPI):
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    validate_catalog()
    yield


app = FastAPI(title="CKA Exam Simulator", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"ok": True}


@app.get("/api/tasks")
async def list_tasks():
    """Lobby summary of the question bank (not a specific exam draw)."""
    return bank_summary()


@app.post("/api/sessions")
async def start_session():
    try:
        session = await create_session()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return session_public(session)


@app.get("/api/sessions/{session_id}")
async def get_session_status(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return session_public(session)


@app.get("/api/sessions/{session_id}/tasks")
async def get_session_tasks(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    return {"tasks": [t.to_public_dict() for t in session.tasks]}


@app.post("/api/sessions/{session_id}/end")
async def finish_session(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="session not found")
    try:
        score = await end_session(session_id, cleanup=True)
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return score


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    await destroy_session(session_id)
    return {"ok": True}


@app.websocket("/ws/terminal/{session_id}")
async def ws_terminal(websocket: WebSocket, session_id: str):
    await terminal_websocket(websocket, session_id)
