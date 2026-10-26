"""ElevenLabs TTS for bedtime reflection – optional, graceful without key."""

from __future__ import annotations

import os
from typing import Optional

import requests

from config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL


def is_voice_available() -> bool:
    return bool(ELEVENLABS_API_KEY and ELEVENLABS_API_KEY.strip())


def synthesize_bedtime(text: str, voice_id: Optional[str] = None) -> Optional[bytes]:
    """
    Generate MP3 audio of the bedtime reflection via ElevenLabs.
    Returns audio bytes, or None if key missing / request fails.
    """
    key = ELEVENLABS_API_KEY.strip() if ELEVENLABS_API_KEY else ""
    if not key or not text.strip():
        return None

    vid = voice_id or ELEVENLABS_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{vid}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": key,
    }
    payload = {
        "text": text.strip(),
        "model_id": ELEVENLABS_MODEL,
        "voice_settings": {
            "stability": 0.55,
            "similarity_boost": 0.7,
            "style": 0.15,
            "use_speaker_boost": True,
        },
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=45)
        if r.status_code == 200 and r.content:
            return r.content
    except Exception:
        pass
    return None
