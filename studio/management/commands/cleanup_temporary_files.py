from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
import time


class Command(BaseCommand):
    help = "Remove files in MEDIA_ROOT/projects/*/temporary older than N days."

    def add_arguments(self, parser):
        parser.add_argument("--days", type=int, default=7)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        cutoff = time.time() - options["days"] * 86400
        root = Path(settings.MEDIA_ROOT) / "projects"
        if not root.exists():
            return
        for temp in root.glob("*/temporary"):
            for f in temp.rglob("*"):
                if f.is_file() and f.stat().st_mtime < cutoff:
                    self.stdout.write(f"{'[dry] ' if options['dry_run'] else ''}{f}")
                    if not options["dry_run"]:
                        f.unlink()
