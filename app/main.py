"""Web server: serves the chat page and the /api/chat endpoint."""
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .agent import handle_message
from .state import reset_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")

app = FastAPI(title="SuperChat")
STATIC = Path(__file__).parent / "static"


class ChatIn(BaseModel):
    session_id: str
    message: str


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


@app.post("/api/chat")
def chat(body: ChatIn):
    return handle_message(body.session_id, body.message)


@app.post("/api/reset")
def reset(body: ChatIn):
    reset_session(body.session_id)
    return {"ok": True}
