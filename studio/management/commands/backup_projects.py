"""
Backs up all project metadata (JSON) and referenced images to a ZIP archive.
Usage:
    python manage.py backup_projects --out backups/lekha-YYYYMMDD.zip
    python manage.py backup_projects --out b.zip --include-exports
"""
import json
import zipfile
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core import serializers

from studio.models import Project


class Command(BaseCommand):
    help = "Back up project metadata + source images to a ZIP archive."

    def add_arguments(self, parser):
        parser.add_argument("--out", required=True, help="Output ZIP path.")
        parser.add_argument("--include-exports", action="store_true",
                            help="Also include generated DOCX files.")

    def handle(self, *args, **options):
        out = Path(options["out"])
        out.parent.mkdir(parents=True, exist_ok=True)
        media_root = Path(settings.MEDIA_ROOT).resolve()

        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            manifest = {
                "created_at": datetime.utcnow().isoformat() + "Z",
                "project_count": Project.objects.count(),
                "projects": [],
            }
            for p in Project.objects.all().iterator():
                meta = {
                    "id": str(p.id),
                    "title": p.title,
                    "status": p.status,
                    "source_images": p.source_images,
                    "page_metadata": p.page_metadata,
                    "design_options": p.design_options,
                    "project_settings": p.project_settings,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                }
                manifest["projects"].append(meta)

                # Add source images
                for img in (p.source_images or []):
                    rel = img.get("stored_path")
                    if not rel:
                        continue
                    try:
                        src = (media_root / rel).resolve()
                        src.relative_to(media_root)  # safety
                    except (ValueError, FileNotFoundError):
                        continue
                    if src.exists():
                        z.write(src, arcname=f"media/{rel}")

                if options["include_exports"]:
                    for e in (p.export_history or []):
                        rel = e.get("relative_path")
                        if not rel:
                            continue
                        try:
                            src = (media_root / rel).resolve()
                            src.relative_to(media_root)
                        except (ValueError, FileNotFoundError):
                            continue
                        if src.exists():
                            z.write(src, arcname=f"media/{rel}")

            # Full project data as JSON (source of truth for restore)
            data = serializers.serialize(
                "json",
                Project.objects.all(),
                fields=("title", "description", "status", "source_images",
                        "extracted_text", "edited_text", "structured_content",
                        "page_metadata", "processing_options", "design_options",
                        "revision_history", "export_history", "project_settings",
                        "created_at", "updated_at", "completed_at", "error_message"),
            )
            z.writestr("projects.json", data)
            z.writestr("manifest.json", json.dumps(manifest, indent=2))

        self.stdout.write(self.style.SUCCESS(f"Backup written: {out}"))
