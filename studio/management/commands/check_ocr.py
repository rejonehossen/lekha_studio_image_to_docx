from django.core.management.base import BaseCommand
from studio.services.ocr_providers import TesseractProvider


class Command(BaseCommand):
    help = "Diagnose OCR engine availability."

    def handle(self, *args, **options):
        t = TesseractProvider()
        if not t.is_available():
            self.stderr.write("Tesseract binary NOT found on PATH.")
            return
        langs = t.installed_langs()
        self.stdout.write(f"Tesseract available. Languages: {', '.join(langs) or '(none)'}")
        if "ben" not in langs:
            self.stderr.write("Bangla language data (ben) missing. Install tesseract-ocr-ben.")
        if "eng" not in langs:
            self.stderr.write("English language data (eng) missing.")




