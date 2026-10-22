"""
Core agent logic for SlothCloser.
- Tries local Ollama first (best experience)
- Falls back to a high-quality offline response if Ollama is unavailable
  (so the public Render demo always works)
"""

import re
import ollama
from config import DEFAULT_MODEL, TEMPERATURE
from prompts import SYSTEM_PROMPT, SUMMARY_PROMPT, TASKS_PROMPT, BEDTIME_PROMPT


class SlothAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def _chat(self, prompt: str, max_tokens: int = 200):
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
        """Gentle rule-based summary when no model is available."""
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
        """Extract possible remaining tasks with simple heuristics."""
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
            bullets = "\n".join(f"• {c}" for c in candidates[:4])
            return bullets

        return "Nothing clearly left open. The day looks complete."

    def _fallback_bedtime(self, notes: str) -> str:
        """Warm offline bedtime reflection."""
        return (
            "The day is finished, even if a few threads remain. "
            "You showed up, did what you could, and that is enough. "
            "Let the remaining pieces wait until morning. "
            "For now, the only task left is to rest. "
            "Sleep well — tomorrow will meet you when you are ready."
        )

    def summarize_day(self, notes: str) -> str:
        prompt = SUMMARY_PROMPT.format(notes=notes.strip())
        result = self._chat(prompt, max_tokens=180)
        return result if result else self._fallback_summary(notes)

    def extract_open_loops(self, notes: str) -> str:
        prompt = TASKS_PROMPT.format(notes=notes.strip())
        result = self._chat(prompt, max_tokens=150)
        return result if result else self._fallback_open_loops(notes)

    def write_bedtime(self, notes: str) -> str:
        prompt = BEDTIME_PROMPT.format(notes=notes.strip())
        result = self._chat(prompt, max_tokens=220)
        return result if result else self._fallback_bedtime(notes)

    def close_day(self, notes: str) -> dict:
        """Run the full closing ritual."""
        if not notes or not notes.strip():
            return {
                "summary": "No notes provided.",
                "open_loops": "Nothing to close.",
                "bedtime": "Rest well. Tomorrow will wait for you.",
            }

        return {
            "summary": self.summarize_day(notes),
            "open_loops": self.extract_open_loops(notes),
            "bedtime": self.write_bedtime(notes),
        }


def list_available_models() -> list:
    """Return models currently available in Ollama (works across library versions)."""
    try:
        result = ollama.list()
        models = []
        if isinstance(result, dict):
            models = result.get("models", [])
        else:
            models = getattr(result, "models", []) or []

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