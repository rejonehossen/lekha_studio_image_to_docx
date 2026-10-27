"""
Normalization helpers. We deliberately do NOT apply aggressive Unicode
normalization that could merge or reorder Bangla combining marks. NFC is safe.
"""

import unicodedata


def normalize_text(text: str) -> str:
    """Apply safe NFC normalization only."""
    return unicodedata.normalize("NFC", text)


def detect_script(text: str) -> str:
    """Very lightweight script sniff: bangla / english / mixed / empty."""
    has_bengali = any("\u0980" <= ch <= "\u09FF" for ch in text)
    has_latin = any("a" <= ch.lower() <= "z" for ch in text)
    if has_bengali and has_latin:
        return "mixed"
    if has_bengali:
        return "bangla"
    if has_latin:
        return "english"
    return "empty"
