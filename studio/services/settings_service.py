"""
Diagnostics for OCR/font availability. Does not persist a separate model;
global settings are read from settings.py / env. Project-level settings live
inside Project.project_settings JSON.
"""
import shutil


def ocr_diagnostics() -> dict:
    from .ocr_providers import TesseractProvider
    t = TesseractProvider()
    return {
        "tesseract_binary": t.is_available(),
        "installed_languages": t.installed_langs(),
    }


def known_fonts_hint() -> list:
    """
    Cannot reliably detect installed fonts cross-platform in Python.
    Return commonly-expected names for user reference.
    """
    return [
        "Noto Serif Bengali",
        "Noto Sans Bengali",
        "Kalpurush",
        "SolaimanLipi",
        "Noto Serif",
        "Noto Sans",
    ]
