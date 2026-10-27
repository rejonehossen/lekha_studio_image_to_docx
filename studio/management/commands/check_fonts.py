
from django.core.management.base import BaseCommand
from studio.services.settings_service import known_fonts_hint


class Command(BaseCommand):
    help = "Show commonly expected Bangla/Latin font names. Cannot reliably enumerate OS fonts cross-platform."

    def handle(self, *args, **options):
        self.stdout.write("Commonly expected fonts (verify installation manually):")
        for f in known_fonts_hint():
            self.stdout.write(f"  - {f}")
        self.stdout.write("")
        self.stdout.write(
            "Note: fonts are referenced by name in the DOCX. They are NOT embedded. "
            "The machine that opens the file must have them installed."
        )





