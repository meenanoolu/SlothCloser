"""
Core agent logic for SlothCloser.
- Tries local Ollama + open-weight model first (best experience)
- Falls back to a high-quality offline response if Ollama is unavailable
  (so the public Render demo always works and never crashes)
- Supports optional mood to gently shape the bedtime reflection
"""

import re
from datetime import datetime
from typing import Optional

import ollama
from config import DEFAULT_MODEL, TEMPERATURE
from prompts import (
    SYSTEM_PROMPT,
    SUMMARY_PROMPT,
    TASKS_PROMPT,
    BEDTIME_PROMPT,
    MOOD_INSTRUCTIONS,
)


class SlothAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.used_fallback = False

    def _chat(self, prompt: str, max_tokens: int = 200) -> Optional[str]:
        """Try to talk to the local model. Returns None on failure."""
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
            return response["message"]["content"].strip()
        except Exception:
            return None

    def _fallback_summary(self, notes: str) -> str:
        lines = [l.strip() for l in notes.strip().split("\n") if l.strip()]
        if not lines:
            return "A quiet day. Nothing much needed to be written down."

        preview = " ".join(lines[:3])
        if len(preview) > 140:
            preview = preview[:137] + "..."

        return (
            f"Today held a few quiet moments and small movements. "
            f"You noted: {preview} "
            f"Overall it feels like a day that asked for patience more than speed."
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
            return "\n".join(f"• {c}" for c in candidates[:4])

        return "Nothing clearly left open. The day looks complete."

    def _fallback_bedtime(self, notes: str, mood: str = "neutral") -> str:
        base = (
            "The day is finished, even if a few threads remain. "
            "You showed up, did what you could, and that is enough. "
            "Let the remaining pieces wait until morning. "
            "For now, the only task left is to rest. "
            "Sleep well — tomorrow will meet you when you are ready."
        )

        if mood == "tired":
            return (
                "You are tired, and that is information worth listening to. "
                "The day does not need any more effort from you tonight. "
                "Whatever is unfinished can wait in the quiet. "
                "Rest is not a reward — it is part of the work. "
                "Sleep well."
            )
        if mood == "heavy":
            return (
                "Some days feel heavier than others. This seems to be one of them. "
                "You do not have to solve anything right now. "
                "The weight can sit beside you without being fixed. "
                "Morning will come regardless. "
                "For now, just set it down."
            )
        if mood == "light":
            return (
                "There is a quiet ease in the way this day ends. "
                "Nothing dramatic, just a soft landing. "
                "Hold on to that lightness for a moment. "
                "It does not need to be earned or explained. "
                "Rest easy."
            )
        if mood == "grateful":
            return (
                "Gratitude does not have to be loud. "
                "Even a small, quiet thank-you is enough. "
                "Whatever good found its way to you today can stay with you into the night. "
                "Sleep with that softness nearby."
            )
        return base

    def summarize_day(self, notes: str) -> str:
        prompt = SUMMARY_PROMPT.format(notes=notes.strip())
        result = self._chat(prompt, max_tokens=180)
        if result is None:
            self.used_fallback = True
            return self._fallback_summary(notes)
        return result

    def extract_open_loops(self, notes: str) -> str:
        prompt = TASKS_PROMPT.format(notes=notes.strip())
        result = self._chat(prompt, max_tokens=150)
        if result is None:
            self.used_fallback = True
            return self._fallback_open_loops(notes)
        return result

    def write_bedtime(self, notes: str, mood: str = "neutral") -> str:
        mood_instruction = MOOD_INSTRUCTIONS.get(mood, "")
        if mood_instruction:
            mood_instruction = f"\n- {mood_instruction}"

        prompt = BEDTIME_PROMPT.format(
            notes=notes.strip(),
            mood_instruction=mood_instruction,
        )
        result = self._chat(prompt, max_tokens=220)
        if result is None:
            self.used_fallback = True
            return self._fallback_bedtime(notes, mood)
        return result

    def close_day(self, notes: str, mood: str = "neutral") -> dict:
        """Run the full closing ritual."""
        self.used_fallback = False

        if not notes or not notes.strip():
            return {
                "summary": "No notes provided.",
                "open_loops": "Nothing to close.",
                "bedtime": "Rest well. Tomorrow will wait for you.",
                "used_fallback": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "mood": mood,
            }

        summary = self.summarize_day(notes)
        open_loops = self.extract_open_loops(notes)
        bedtime = self.write_bedtime(notes, mood=mood)

        return {
            "summary": summary,
            "open_loops": open_loops,
            "bedtime": bedtime,
            "used_fallback": self.used_fallback,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
        }


def list_available_models() -> list:
    """Return models currently available in Ollama (works across library versions)."""
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