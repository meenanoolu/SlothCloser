"""Configuration for SlothCloser – calm local evening wind-down agent."""

import os
from pathlib import Path

# Primary open-weight model (Gemma family preferred for the challenge)
DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "gemma2:2b")

# Soft temperature for calm, steady responses
TEMPERATURE = 0.55

# App branding
APP_TITLE = "SlothCloser"
APP_SUBTITLE = "Your calm local agent that closes the day for you"
APP_ICON = "🦥"
APP_VERSION = "1.1.0"

# Paths
BASE_DIR = Path(__file__).parent
HISTORY_DIR = BASE_DIR / "closings"
HISTORY_DIR.mkdir(exist_ok=True)

# Mood options shown in the UI
MOODS = {
    "neutral": "Quiet / Neutral",
    "tired": "Tired",
    "heavy": "Heavy / Overwhelmed",
    "light": "Light / Content",
    "grateful": "Grateful",
}

# Challenge context
CHALLENGE_TAG = "Hacktoberfest Open-Source AI Challenge Week 3: Slow and Steady"

# Partner categories this project genuinely uses or is ready for
PARTNERS = [
    "Gemma (open-weight core)",
    "Render (hosting + Blueprint)",
    "Ollama (local inference)",
    "ElevenLabs-ready (voice bedtime reflection)",
    "MongoDB Atlas-ready (closing history)",
]