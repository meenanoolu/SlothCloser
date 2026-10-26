"""Warmer, slower bedtime voice via edge-tts (no API key)."""

from __future__ import annotations

import asyncio
import concurrent.futures
import tempfile
from pathlib import Path
from typing import Optional

# Soft, slower neural voices (tried in order)
VOICES = [
    "en-US-AriaNeural",      # warm, clear
    "en-GB-SoniaNeural",     # soft British
    "en-US-JennyNeural",     # fallback
]


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=90)
    return asyncio.run(coro)


async def _edge_save(text: str, path: str, voice: str) -> None:
    import edge_tts
    # Slower rate + slightly lower pitch = calmer bedtime feel
    communicate = edge_tts.Communicate(
        text.strip()[:2500],
        voice,
        rate="-12%",
        pitch="-4Hz",
    )
    await communicate.save(path)


def synthesize(text: str) -> Optional[bytes]:
    if not text or not text.strip():
        return None
    # Prefer speaking reflection + poem + quote as one soft piece
    for voice in VOICES:
        try:
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                path = tmp.name
            _run_async(_edge_save(text, path, voice))
            data = Path(path).read_bytes()
            Path(path).unlink(missing_ok=True)
            if len(data) > 100:
                return data
        except Exception:
            continue
    return None