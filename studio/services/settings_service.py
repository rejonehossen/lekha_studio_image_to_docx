"""Diagnostics for OCR and optional capability detection."""
import shutil


def ocr_diagnostics() -> dict:
    from .ocr_providers import TesseractProvider
    t = TesseractProvider()
    return {
        "tesseract_binary": t.is_available(),
        "installed_languages": t.installed_langs(),
        "bangla_available": "ben" in t.installed_langs(),
        "english_available": "eng" in t.installed_langs(),
    }


def known_fonts_hint() -> list:
    return [
        "Noto Serif Bengali",
        "Noto Sans Bengali",
        "Kalpurush",
        "SolaimanLipi",
        "Noto Serif",
        "Noto Sans",
    ]


def storage_info(media_root) -> dict:
    from pathlib import Path
    root = Path(media_root)
    total = 0
    files = 0
    if root.exists():
        for p in root.rglob("*"):
            if p.is_file():
                files += 1
                total += p.stat().st_size
    return {"files": files, "bytes": total}
