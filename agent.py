"""
Core agent for SlothCloser.
- One structured Ollama call (fast) instead of five sequential calls
- High-quality offline fallbacks when no model is available
- Local JSON history (MongoDB Atlas–ready document shape)
"""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import DEFAULT_MODEL, TEMPERATURE, HISTORY_DIR
from prompts import SYSTEM_PROMPT, CLOSE_DAY_PROMPT, MOOD_INSTRUCTIONS

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class SlothAgent:
    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model
        self.used_fallback = False

    def _chat(self, prompt: str, max_tokens: int = 420) -> Optional[str]:
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
            return response["message"]["content"].strip()
        except Exception:
            return None

    # ---------- Offline fallbacks (instant) ----------
    def _fallback(self, notes: str, mood: str) -> dict:
        lines = [l.strip() for l in notes.strip().split("\n") if l.strip()]
        preview = " ".join(lines[:2]) if lines else ""
        if len(preview) > 110:
            preview = preview[:107] + "..."

        summary = (
            f"Today moved at its own pace. You noted: {preview} "
            f"It feels like a day that preferred patience over speed."
            if preview
            else "A quiet day. Nothing much needed to be written down."
        )

        # Simple open-loop extraction
        text = notes.lower()
        candidates = []
        for pattern in [
            r"(still need to|need to|have to|should|must|todo|to-do|remember to)\s+([^.!\n]+)",
            r"(reply to|email|message|call|finish|complete|send|write)\s+([^.!\n]+)",
        ]:
            for m in re.finditer(pattern, text):
                item = m.group(0).strip().capitalize()
                if len(item) > 8 and item not in candidates:
                    candidates.append(item)
        open_loops = (
            "\n".join(f"• {c}" for c in candidates[:3])
            if candidates
            else "Nothing open. The day is complete."
        )

        bedtime_map = {
            "tired": (
                "You are tired, and that is information worth listening to. "
                "The day does not need any more effort from you tonight. "
                "Whatever is unfinished can wait in the quiet. "
                "Rest is not a reward — it is part of the work. Sleep well."
            ),
            "heavy": (
                "Some days feel heavier than others. This seems to be one of them. "
                "You do not have to solve anything right now. "
                "The weight can sit beside you without being fixed. "
                "Morning will come regardless. For now, just set it down."
            ),
            "light": (
                "There is a quiet ease in the way this day ends. "
                "Nothing dramatic, just a soft landing. "
                "Hold on to that lightness for a moment. Rest easy."
            ),
            "grateful": (
                "Gratitude does not have to be loud. "
                "Even a small, quiet thank-you is enough. "
                "Whatever good found its way to you today can stay with you into the night."
            ),
        }
        bedtime = bedtime_map.get(
            mood,
            "The day is finished, even if a few threads remain. "
            "You showed up, did what you could, and that is enough. "
            "Let the remaining pieces wait until morning. Sleep well.",
        )

        ambient_map = {
            "tired": "Soft rain on a quiet window, distant thunder very far away, a single candle flame.",
            "heavy": "Low wind through pine trees at night, occasional creak of wood, deep steady breathing.",
            "light": "Early morning birds far off, a slow stream over smooth stones, warm light through curtains.",
            "grateful": "Gentle evening breeze through open windows, soft leaves, a distant soft laugh.",
        }
        ambient = ambient_map.get(
            mood, "Quiet room at night, distant rain, the low hum of a house settling into sleep."
        )

        return {
            "summary": summary,
            "open_loops": open_loops,
            "bedtime": bedtime,
            "tomorrow": "Nothing urgent. Let tomorrow arrive gently.",
            "ambient": ambient,
        }

    def _parse_structured(self, raw: str) -> Optional[dict]:
        """Parse the single structured response into sections."""
        try:
            sections = {}
            current = None
            buf = []
            for line in raw.splitlines():
                upper = line.strip().upper()
                if upper.startswith("SUMMARY:"):
                    if current and buf:
                        sections[current] = "\n".join(buf).strip()
                    current = "summary"
                    rest = line.split(":", 1)[-1].strip()
                    buf = [rest] if rest else []
                elif upper.startswith("OPEN:"):
                    if current and buf:
                        sections[current] = "\n".join(buf).strip()
                    current = "open_loops"
                    rest = line.split(":", 1)[-1].strip()
                    buf = [rest] if rest else []
                elif upper.startswith("BEDTIME:"):
                    if current and buf:
                        sections[current] = "\n".join(buf).strip()
                    current = "bedtime"
                    rest = line.split(":", 1)[-1].strip()
                    buf = [rest] if rest else []
                elif upper.startswith("TOMORROW:"):
                    if current and buf:
                        sections[current] = "\n".join(buf).strip()
                    current = "tomorrow"
                    rest = line.split(":", 1)[-1].strip()
                    buf = [rest] if rest else []
                elif upper.startswith("AMBIENT:"):
                    if current and buf:
                        sections[current] = "\n".join(buf).strip()
                    current = "ambient"
                    rest = line.split(":", 1)[-1].strip()
                    buf = [rest] if rest else []
                else:
                    if current is not None:
                        buf.append(line)
            if current and buf:
                sections[current] = "\n".join(buf).strip()

            required = ["summary", "open_loops", "bedtime", "tomorrow", "ambient"]
            if all(k in sections and sections[k] for k in required):
                return sections
        except Exception:
            pass
        return None

    def close_day(self, notes: str, mood: str = "neutral") -> dict:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.used_fallback = False

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

        mood_instruction = MOOD_INSTRUCTIONS.get(mood, "")
        if mood_instruction:
            mood_instruction = f"\nMood note: {mood_instruction}"

        prompt = CLOSE_DAY_PROMPT.format(
            notes=notes.strip(),
            mood_instruction=mood_instruction,
        )

        raw = self._chat(prompt, max_tokens=420)
        if raw:
            parsed = self._parse_structured(raw)
            if parsed:
                return {
                    **parsed,
                    "used_fallback": False,
                    "timestamp": ts,
                    "mood": mood,
                }

        # Fallback path
        self.used_fallback = True
        fb = self._fallback(notes, mood)
        return {
            **fb,
            "used_fallback": True,
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


# ---------- Local history (MongoDB Atlas–ready document shape) ----------
def save_closing(result: dict, notes: str) -> Path:
    """Persist a closing as a JSON document. Shape is ready for Atlas."""
    HISTORY_DIR.mkdir(exist_ok=True)
    doc = {
        "_id": str(uuid.uuid4()),
        "timestamp": result["timestamp"],
        "mood": result.get("mood", "neutral"),
        "notes": notes,
        "summary": result.get("summary", ""),
        "open_loops": result.get("open_loops", ""),
        "bedtime": result.get("bedtime", ""),
        "tomorrow": result.get("tomorrow", ""),
        "ambient": result.get("ambient", ""),
        "used_fallback": result.get("used_fallback", False),
        "created_at": datetime.utcnow().isoformat() + "Z",
    }
    safe_ts = result["timestamp"].replace(" ", "_").replace(":", "")
    path = HISTORY_DIR / f"closing_{safe_ts}_{doc['_id'][:8]}.json"
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_recent_closings(limit: int = 12) -> list:
    """Load recent local closings (newest first)."""
    if not HISTORY_DIR.exists():
        return []
    files = sorted(HISTORY_DIR.glob("closing_*.json"), reverse=True)
    out = []
    for f in files[:limit]:
        try:
            out.append(json.loads(f.read_text(encoding="utf-8")))
        except Exception:
            continue
    return out
