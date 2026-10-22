"""Configuration for SlothCloser."""

import os
from pathlib import Path

# Default model – change this to whatever you have pulled in Ollama
DEFAULT_MODEL = os.getenv("SLOTH_MODEL", "gemma2:2b")

# Soft temperature for calm, steady responses
TEMPERATURE = 0.6

# Max tokens for each section
MAX_TOKENS_SUMMARY = 180
MAX_TOKENS_TASKS = 150
MAX_TOKENS_BEDTIME = 220

# App title & branding
APP_TITLE = "SlothCloser"
APP_SUBTITLE = "Slow & steady evening closer"
APP_ICON = "🦥"

# Paths
BASE_DIR = Path(__file__).parent