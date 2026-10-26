"""
SlothCloser API + static frontend
FastAPI · Ollama/Gemma · local history
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent import (SlothAgent, list_available_models, load_recent_closings,
                   save_closing)
from config import (APP_TITLE, APP_VERSION, DEFAULT_MODEL, HISTORY_DIR,
                    MOODS, STATIC_DIR)

app = FastAPI(title=APP_TITLE, version=APP_VERSION)

STATIC_DIR.mkdir(exist_ok=True)
HISTORY_DIR.mkdir(exist_ok=True)


class CloseRequest(BaseModel):
    notes: str = Field(..., min_length=1)
    mood: str = "neutral"
    model: Optional[str] = None


class CloseResponse(BaseModel):
    summary: str
    open_loops: str
    bedtime: str
    poem: str = ""
    quote: str = ""
    tomorrow: str
    ambient: str
    used_fallback: bool
    timestamp: str
    mood: str


@app.get("/api/health")
def health():
    models = list_available_models()
    return {
        "ok": True,
        "version": APP_VERSION,
        "models": models,
        "default_model": DEFAULT_MODEL,
        "local_ready": len(models) > 0,
    }


@app.get("/api/models")
def models():
    available = list_available_models()
    preferred = DEFAULT_MODEL
    if available:
        gemma = [m for m in available if "gemma" in m.lower()]
        preferred = gemma[0] if gemma else available[0]
    return {"models": available, "preferred": preferred}


@app.get("/api/moods")
def moods():
    return {"moods": [{"id": k, "label": v} for k, v in MOODS.items()]}


@app.post("/api/close", response_model=CloseResponse)
def close_day(body: CloseRequest):
    model = body.model or DEFAULT_MODEL
    agent = SlothAgent(model=model)
    result = agent.close_day(body.notes, mood=body.mood)
    try:
        save_closing(result, body.notes)
    except Exception:
        pass
    return CloseResponse(**{
        "summary": result["summary"],
        "open_loops": result["open_loops"],
        "bedtime": result["bedtime"],
        "poem": result.get("poem", ""),
        "quote": result.get("quote", ""),
        "tomorrow": result["tomorrow"],
        "ambient": result["ambient"],
        "used_fallback": result.get("used_fallback", False),
        "timestamp": result["timestamp"],
        "mood": result.get("mood", body.mood),
    })




@app.get("/api/history")
def history(limit: int = 15):
    return {"closings": load_recent_closings(limit)}


@app.get("/api/example")
def example():
    path = Path(__file__).parent / "example-notes.md"
    if path.exists():
        return {"notes": path.read_text(encoding="utf-8")}
    return {"notes": ""}


# Static frontend
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def index():
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(404, "Frontend not found")
    return FileResponse(index_path)