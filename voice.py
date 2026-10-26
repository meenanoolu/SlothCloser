"""Free neural bedtime voice via edge-tts (no API key)."""

from __future__ import annotations

import asyncio
import concurrent.futures
import tempfile
from pathlib import Path
from typing import Optional


def _run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    if loop and loop.is_running():
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, coro).result(timeout=90)
    return asyncio.run(coro)


async def _edge_save(text: str, path: str, voice: str = "en-US-JennyNeural") -> None:
    import edge_tts
    await edge_tts.Communicate(text.strip()[:2500], voice).save(path)


def synthesize(text: str) -> Optional[bytes]:
    if not text or not text.strip():
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