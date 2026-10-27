"""
Restores projects from a backup ZIP created by backup_projects.
Safety: refuses to overwrite by default.
Usage:
    python manage.py restore_project_backup --in b.zip
    python manage.py restore_project_backup --in b.zip --overwrite
"""
import json
import zipfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from studio.models import Project


class Command(BaseCommand):
    help = "Restore projects from a backup ZIP."

    def add_arguments(self, parser):
        parser.add_argument("--in", dest="infile", required=True)
        parser.add_argument("--overwrite", action="store_true")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        infile = Path(options["infile"])
        if not infile.exists():
            raise CommandError(f"File not found: {infile}")

        with zipfile.ZipFile(infile) as z:
            names = set(z.namelist())
            if "projects.json" not in names:
                raise CommandError("Backup missing projects.json")

            # Validate all members: reject path traversal
            media_root = Path(settings.MEDIA_ROOT).resolve()
            for n in names:
                if n.startswith("media/"):
                    target = (media_root / n[len("media/"):]).resolve()
                    if not str(target).startswith(str(media_root)):
                        raise CommandError(f"Refusing unsafe path in archive: {n}")

            projects_data = json.loads(z.read("projects.json"))

            created = 0
            restored_images = 0
            for obj in projects_data:
                fields = obj["fields"]
                old_id = obj["pk"]

                if options["dry_run"]:
                    self.stdout.write(f"[dry] would restore: {fields['title']} ({old_id})")
                    continue

                with transaction.atomic():
                    existing = Project.objects.filter(pk=old_id).first()
                    if existing and not options["overwrite"]:
                        self.stdout.write(self.style.WARNING(
                            f"Skipping {fields['title']} ({old_id}) — exists. Use --overwrite."
                        ))
                        continue
                    p, _ = Project.objects.update_or_create(
                        pk=old_id, defaults={**fields}
                    )
                    created += 1

                # Restore images
                for img in (p.source_images or []):
                    rel = img.get("stored_path")
                    if not rel:
                        continue
                    member = f"media/{rel}"
                    if member not in names:
                        continue
                    dest = (media_root / rel).resolve()
                    if not str(dest).startswith(str(media_root)):
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with z.open(member) as src, open(dest, "wb") as dst:
                        dst.write(src.read())
                    restored_images += 1

        if not options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(
                f"Restored {created} project(s), {restored_images} image file(s)."
            ))
