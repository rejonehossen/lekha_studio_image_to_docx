"""
Language and script helpers. NFC normalization only — we do NOT apply
aggressive Unicode forms that could reorder Bangla combining marks.
"""

import unicodedata


def normalize_text(text: str) -> str:
    return unicodedata.normalize("NFC", text)


def detect_script(text: str) -> str:
    """Return 'bangla', 'english', 'mixed', or 'empty'."""
    has_bengali = any("\u0980" <= ch <= "\u09FF" for ch in text)
    has_latin = any("a" <= ch.lower() <= "z" for ch in text)
    if has_bengali and has_latin:
        return "mixed"
    if has_bengali:
        return "bangla"
    if has_latin:
        return "english"
    return "empty"


def is_safe_for_filename(text: str) -> bool:
    """Reject control chars and path separators; allow Unicode letters."""
    if not text:
        return False
    for ch in text:
        if ch in "/\\" or ord(ch) < 32:
            return False
    return True
