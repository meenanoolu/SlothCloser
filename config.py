"""Configuration for SlothCloser."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "gemma2:2b")
TEMPERATURE = 0.55

APP_TITLE = "SlothCloser"
APP_SUBTITLE = "Your calm local agent that closes the day for you"
APP_ICON = "🦥"
APP_VERSION = "2.0.0"

BASE_DIR = Path(__file__).parent
HISTORY_DIR = BASE_DIR / "closings"
STATIC_DIR = BASE_DIR / "static"
HISTORY_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)

MOODS = {
    "neutral": "Quiet / Neutral",
    "tired": "Tired",
    "heavy": "Heavy / Overwhelmed",
    "light": "Light / Content",
    "grateful": "Grateful",
}

CHALLENGE_TAG = "Hacktoberfest Open-Source AI Challenge · Week 3: Slow and Steady"