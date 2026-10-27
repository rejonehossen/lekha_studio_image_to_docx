import shutil
import os
from dataclasses import dataclass
from typing import Optional

import pytesseract
from PIL import Image

# Explicitly set the path to where Tesseract is installed on Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

@dataclass
class OCRResult:
    text: str
    engine: str
    lang: str
    confidence: Optional[float] = None
    error: Optional[str] = None

class ProviderUnavailable(Exception):
    pass

class TesseractProvider:
    name = "tesseract"

    def __init__(self):
        self._available = None

    def is_available(self) -> bool:
        if self._available is None:
            # Check if the explicit path exists
            if os.path.exists(pytesseract.pytesseract.tesseract_cmd):
                self._available = True
            else:
                # Fallback to checking the system PATH
                self._available = shutil.which("tesseract") is not None
        return self._available

    def installed_langs(self) -> list:
        if not self.is_available():
            return []
        try:
            return sorted(pytesseract.get_languages(config=""))
        except Exception:
            return []

    def lang_string(self, mode: str) -> str:
        """Map app language mode to Tesseract lang code, respecting installed langs."""
        installed = set(self.installed_langs())
        if mode == "bangla":
            if "ben" not in installed:
                raise ProviderUnavailable(
                    "Bangla language data for Tesseract is not installed (ben). "
                    "Install tesseract-ocr-ben or the equivalent."
                )
            return "ben"
        if mode == "english":
            return "eng"
        if mode == "mixed":
            parts = [p for p in ("ben", "eng") if p in installed]
            if not parts:
                raise ProviderUnavailable("No Tesseract language data (eng/ben) installed.")
            return "+".join(parts)
        # auto
        parts = [p for p in ("eng", "ben") if p in installed]
        return "+".join(parts) if parts else "eng"

    def recognize(self, image_path, mode: str = "auto") -> OCRResult:
        if not self.is_available():
            return OCRResult(text="", engine=self.name, lang=mode,
                             error="Tesseract binary not found.")
        try:
            lang = self.lang_string(mode)
        except ProviderUnavailable as e:
            return OCRResult(text="", engine=self.name, lang=mode, error=str(e))
        try:
            with Image.open(image_path) as img:
                text = pytesseract.image_to_string(img, lang=lang)
            return OCRResult(text=text, engine=self.name, lang=lang)
        except Exception as e:
            return OCRResult(text="", engine=self.name, lang=mode, error=str(e))


def get_provider(name: str = "tesseract"):
    if name == "tesseract":
        return TesseractProvider()
    raise ProviderUnavailable(f"Unknown or unconfigured OCR provider: {name}")




