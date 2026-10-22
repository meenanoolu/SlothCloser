"""Configuration for SlothCloser."""

import os
from pathlib import Path

# Default model – change this to whatever you have pulled in Ollama
DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "gemma2:2b")

# Soft temperature for calm, steady responses
TEMPERATURE = 0.6

# App title & branding
APP_TITLE = "SlothCloser"
APP_SUBTITLE = "Slow & steady evening closer"
APP_ICON = "🦥"

# Paths
BASE_DIR = Path(__file__).parent
HISTORY_DIR = BASE_DIR / "closings"          # local history of past closings

# Mood options shown in the UI
MOODS = {
    "neutral": "Quiet / Neutral",
    "tired": "Tired",
    "heavy": "Heavy / Overwhelmed",
    "light": "Light / Content",
    "grateful": "Grateful",
}