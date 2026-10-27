"""
Light offline spelling fix for messy evening notes.
Uses pyspellchecker — no API, works fully local.
Preserves line breaks and avoids over-correcting short tokens.
"""

from __future__ import annotations

import re
from typing import Optional

try:
    from spellchecker import SpellChecker
    _spell = SpellChecker(distance=1)
    AVAILABLE = True
except ImportError:
    _spell = None
    AVAILABLE = False

# Don't "fix" common informal / diary words
_SKIP = {
    "ok", "okay", "idk", "tbh", "imo", "imho", "rn", "btw", "ngl",
    "gonna", "wanna", "gotta", "kinda", "sorta", "yeah", "yep", "nah",
    "hmm", "ugh", "lol", "haha", "ah", "oh", "wow", "meh",
    "todo", "wip", "asap", "fyi", "nvm", "thx", "pls", "plz",
}


def _fix_word(word: str) -> str:
    if not AVAILABLE or _spell is None:
        return word
    if not word or len(word) < 3:
        return word
    lower = word.lower()
    if lower in _SKIP:
        return word
    # Keep ALL-CAPS acronyms (API, TODO already skipped)
    if word.isupper() and len(word) <= 5:
        return word
    # Already known
    if lower in _spell:
        return word
    correction = _spell.correction(lower)
    if not correction or correction == lower:
        return word
    # Preserve original capitalization pattern
    if word[0].isupper():
        correction = correction[0].upper() + correction[1:]
    if word.isupper():
        correction = correction.upper()
    return correction


def fix_notes(text: str) -> str:
    """
    Correct obvious typos in free-form notes.
    Returns original text if spellchecker unavailable or text empty.
    """
    if not text or not text.strip() or not AVAILABLE:
        return text

    def repl(match: re.Match) -> str:
        return _fix_word(match.group(0))

    # Letters only — leave numbers, punctuation, emoji alone
    return re.sub(r"[A-Za-z']+", repl, text)