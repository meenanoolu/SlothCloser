"""
Core agent logic for SlothCloser.
- Tries local Ollama + open-weight model first (Gemma preferred)
- Falls back to high-quality offline responses if Ollama is unavailable
- Supports mood, "one tiny thing for tomorrow", and ambient prompt
- Designed so private evening thoughts never leave the machine
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from config import DEFAULT_MODEL, TEMPERATURE
from prompts import (
    SYSTEM_PROMPT,
    SUMMARY_PROMPT,
    TASKS_PROMPT,
    BEDTIME_PROMPT,
    TOMORROW_PROMPT,
    AMBIENT_PROMPT,
    MOOD_INSTRUCTIONS,
)

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class SlothAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.used_fallback = False

    def _chat(self, prompt: str, max_tokens: int = 160) -> Optional[str]:
        """Try local model. Returns None on any failure."""
        if not OLLAMA_AVAILABLE:
            return None
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                options={
                    "temperature": TEMPERATURE,
                    "num_predict": max_tokens,
                },
            )
            content = response["message"]["content"].strip()
            # Light cleanup of common model artifacts
            content = re.sub(r"^(Day summary|Remaining open loops|Bedtime reflection|One tiny thing for tomorrow|Ambient soundscape prompt)[:\s]*", "", content, flags=re.I)
            return content
        except Exception:
            return None

    # ---------- Fallbacks (instant, high quality) ----------
    def _fallback_summary(self, notes: str) -> str:
        lines = [l.strip() for l in notes.strip().split("\n") if l.strip()]
        if not lines:
            return "A quiet day. Nothing much needed to be written down."
        preview = " ".join(lines[:2])
        if len(preview) > 120:
            preview = preview[:117] + "..."
        return (
            f"Today moved at its own pace. You noted: {preview} "
            f"It feels like a day that preferred patience over speed."
        )

    def _fallback_open_loops(self, notes: str) -> str:
        text = notes.lower()
        candidates = []
        patterns = [
            r"(still need to|need to|have to|should|must|todo|to-do|remember to)\s+([^.!\n]+)",
            r"(reply to|email|message|call|finish|complete|send|write)\s+([^.!\n]+)",
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text):
                item = match.group(0).strip().capitalize()
                if len(item) > 8 and item not in candidates:
                    candidates.append(item)
        if candidates:
            return "\n".join(f"• {c}" for c in candidates[:3])
        return "Nothing open. The day is complete."

    def _fallback_bedtime(self, mood: str = "neutral") -> str:
        if mood == "tired":
            return (
                "You are tired, and that is information worth listening to. "
                "The day does not need any more effort from you tonight. "
                "Whatever is unfinished can wait in the quiet. "
                "Rest is not a reward — it is part of the work. Sleep well."
            )
        if mood == "heavy":
            return (
                "Some days feel heavier than others. This seems to be one of them. "
                "You do not have to solve anything right now. "
                "The weight can sit beside you without being fixed. "
                "Morning will come regardless. For now, just set it down."
            )
        if mood == "light":
            return (
                "There is a quiet ease in the way this day ends. "
                "Nothing dramatic, just a soft landing. "
                "Hold on to that lightness for a moment. Rest easy."
            )
        if mood == "grateful":
            return (
                "Gratitude does not have to be loud. "
                "Even a small, quiet thank-you is enough. "
                "Whatever good found its way to you today can stay with you into the night."
            )
        return (
            "The day is finished, even if a few threads remain. "
            "You showed up, did what you could, and that is enough. "
            "Let the remaining pieces wait until morning. Sleep well."
        )

    def _fallback_tomorrow(self) -> str:
        return "Nothing urgent. Let tomorrow arrive gently."

    def _fallback_ambient(self, mood: str = "neutral") -> str:
        if mood == "tired":
            return "Soft rain on a quiet window, distant thunder very far away, a single candle flame."
        if mood == "heavy":
            return "Low wind through pine trees at night, occasional creak of wood, deep steady breathing."
        if mood == "light":
            return "Early morning birds far off, a slow stream over smooth stones, warm light through curtains."
        if mood == "grateful":
            return "Gentle evening breeze through open windows, soft leaves, a distant soft laugh."
        return "Quiet room at night, distant rain, the low hum of a house settling into sleep."

    # ---------- Main methods ----------
    def summarize_day(self, notes: str) -> str:
        result = self._chat(SUMMARY_PROMPT.format(notes=notes.strip()), max_tokens=140)
        if result is None:
            self.used_fallback = True
            return self._fallback_summary(notes)
        return result

    def extract_open_loops(self, notes: str) -> str:
        result = self._chat(TASKS_PROMPT.format(notes=notes.strip()), max_tokens=120)
        if result is None:
            self.used_fallback = True
            return self._fallback_open_loops(notes)
        return result

    def write_bedtime(self, notes: str, mood: str = "neutral") -> str:
        mood_instruction = MOOD_INSTRUCTIONS.get(mood, "")
        if mood_instruction:
            mood_instruction = f"\n- {mood_instruction}"
        prompt = BEDTIME_PROMPT.format(notes=notes.strip(), mood_instruction=mood_instruction)
        result = self._chat(prompt, max_tokens=180)
        if result is None:
            self.used_fallback = True
            return self._fallback_bedtime(mood)
        return result

    def one_tiny_thing(self, notes: str) -> str:
        result = self._chat(TOMORROW_PROMPT.format(notes=notes.strip()), max_tokens=60)
        if result is None:
            self.used_fallback = True
            return self._fallback_tomorrow()
        return result

    def ambient_prompt(self, notes: str, mood: str = "neutral") -> str:
        result = self._chat(AMBIENT_PROMPT.format(notes=notes.strip()), max_tokens=50)
        if result is None:
            self.used_fallback = True
            return self._fallback_ambient(mood)
        return result

    def close_day(self, notes: str, mood: str = "neutral") -> dict:
        """Full closing ritual – returns everything needed by the UI."""
        self.used_fallback = False
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")

        if not notes or not notes.strip():
            return {
                "summary": "No notes provided.",
                "open_loops": "Nothing to close.",
                "bedtime": "Rest well. Tomorrow will wait for you.",
                "tomorrow": "Nothing urgent. Let tomorrow arrive gently.",
                "ambient": "Quiet room at night, soft rain in the distance.",
                "used_fallback": False,
                "timestamp": ts,
                "mood": mood,
            }

        # Sequential with tight token limits for speed on small models
        summary = self.summarize_day(notes)
        open_loops = self.extract_open_loops(notes)
        bedtime = self.write_bedtime(notes, mood=mood)
        tomorrow = self.one_tiny_thing(notes)
        ambient = self.ambient_prompt(notes, mood=mood)

        return {
            "summary": summary,
            "open_loops": open_loops,
            "bedtime": bedtime,
            "tomorrow": tomorrow,
            "ambient": ambient,
            "used_fallback": self.used_fallback,
            "timestamp": ts,
            "mood": mood,
        }


def list_available_models() -> list:
    if not OLLAMA_AVAILABLE:
        return []
    try:
        result = ollama.list()
        models = (
            result.get("models", [])
            if isinstance(result, dict)
            else getattr(result, "models", []) or []
        )
        names = []
        for m in models:
            if isinstance(m, dict):
                name = m.get("name") or m.get("model")
            else:
                name = getattr(m, "name", None) or getattr(m, "model", None)
            if name:
                names.append(str(name))
        return names
    except Exception:
        return []