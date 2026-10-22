"""Core agent logic for SlothCloser – talks to local Ollama."""

import ollama
from config import DEFAULT_MODEL, TEMPERATURE
from prompts import SYSTEM_PROMPT, SUMMARY_PROMPT, TASKS_PROMPT, BEDTIME_PROMPT


class SlothAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def _chat(self, prompt: str, max_tokens: int = 200) -> str:
        """Send a single turn to the local model."""
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
        except Exception as e:
            return (
                "⚠️ Could not reach the model.\n\n"
                f"Error: {str(e)}\n\n"
                "Make sure Ollama is running and the model is pulled.\n"
                "Try: ollama serve   then   ollama pull gemma2:2b"
            )

    def summarize_day(self, notes: str) -> str:
        prompt = SUMMARY_PROMPT.format(notes=notes.strip())
        return self._chat(prompt, max_tokens=180)

    def extract_open_loops(self, notes: str) -> str:
        prompt = TASKS_PROMPT.format(notes=notes.strip())
        return self._chat(prompt, max_tokens=150)

    def write_bedtime(self, notes: str) -> str:
        prompt = BEDTIME_PROMPT.format(notes=notes.strip())
        return self._chat(prompt, max_tokens=220)

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


def list_available_models() -> list[str]:
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