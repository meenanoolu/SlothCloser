"""
Bedtime voice for SlothCloser.

1. ElevenLabs if ELEVENLABS_API_KEY is set
2. edge-tts (free, no API key) otherwise — always works for demos

UI never shows developer key instructions.
"""

from __future__ import annotations

import asyncio
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import requests

from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL


def has_elevenlabs() -> bool:
    return bool(ELEVENLABS_API_KEY and str(ELEVENLABS_API_KEY).strip())


def _elevenlabs(text: str) -> Optional[bytes]:
    key = str(ELEVENLABS_API_KEY).strip()
    if not key or not text.strip():
        return None
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": key,
    }
    payload = {
        "text": text.strip()[:2500],
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.6,
            "similarity_boost": 0.75,
            "style": 0.1,
            "use_speaker_boost": True,
        },
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=50)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception:
        return None
    return None


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        # Streamlit already has a loop — run in a new thread with its own loop
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=60)
    return asyncio.run(coro)


async def _edge_save(text: str, path: str, voice: str = "en-US-JennyNeural") -> None:
    import edge_tts
    await edge_tts.Communicate(text.strip()[:2500], voice).save(path)


def _edge_tts(text: str) -> Optional[bytes]:
    if not text.strip():
        return None
    try:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            path = tmp.name
        _run_async(_edge_save(text, path))
        data = Path(path).read_bytes()
        Path(path).unlink(missing_ok=True)
        return data if len(data) > 100 else None
    except Exception:
        return None


def synthesize(text: str) -> Tuple[Optional[bytes], str]:
    """Return (mp3_bytes, provider_name). provider is 'ElevenLabs' or 'Neural voice'."""
    if has_elevenlabs():
        audio = _elevenlabs(text)
        if audio:
            return audio, "ElevenLabs"
    audio = _edge_tts(text)
    if audio:
        return audio, "Neural voice"
    return None, ""
