"""Configuration for SlothCloser – calm local evening wind-down agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "gemma2:2b")
TEMPERATURE = 0.55

# ElevenLabs (optional – set ELEVENLABS_API_KEY in .env or Streamlit secrets)
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  # Rachel – calm default
ELEVENLABS_MODEL = os.getenv("ELEVENLABS_MODEL", "eleven_multilingual_v2")

APP_TITLE = "SlothCloser"
APP_SUBTITLE = "Your calm local agent that closes the day for you"
APP_ICON = "🦥"
APP_VERSION = "1.5.0"

BASE_DIR = Path(__file__).parent
HISTORY_DIR = BASE_DIR / "closings"
HISTORY_DIR.mkdir(exist_ok=True)

MOODS = {
    "neutral": "Quiet / Neutral",
    "tired": "Tired",
    "heavy": "Heavy / Overwhelmed",
    "light": "Light / Content",
    "grateful": "Grateful",
}

CHALLENGE_TAG = "Hacktoberfest Open-Source AI Challenge · Week 3: Slow and Steady"
