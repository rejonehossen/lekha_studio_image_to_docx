from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from studio.services.export_service import validate_docx


class Command(BaseCommand):
    help = "Validate that a .docx file is a real Word ZIP container with required parts."

    def add_arguments(self, parser):
        parser.add_argument("path", type=str)

    def handle(self, *args, **options):
        path = Path(options["path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")
        if validate_docx(path):
            self.stdout.write(self.style.SUCCESS(f"OK: {path}"))
        else:
            raise CommandError(f"Invalid DOCX: {path}")



