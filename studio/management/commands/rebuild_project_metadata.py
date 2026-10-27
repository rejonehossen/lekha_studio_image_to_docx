"""
Recomputes structured_content from edited_text for each project.
Safe: does NOT overwrite edited_text or extracted_text.
Usage:
    python manage.py rebuild_project_metadata
    python manage.py rebuild_project_metadata --project <uuid>
"""
from django.core.management.base import BaseCommand

from studio.models import Project
from studio.services.text_organizer import to_structured


class Command(BaseCommand):
    help = "Rebuild structured_content from edited_text for projects."

    def add_arguments(self, parser):
        parser.add_argument("--project", help="Project UUID (default: all).")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        qs = Project.objects.all()
        if options["project"]:
            qs = qs.filter(pk=options["project"])

        count = 0
        for p in qs.iterator():
            text = p.edited_text or p.extracted_text or ""
            structured = to_structured(text)
            if options["dry_run"]:
                self.stdout.write(f"[dry] {p.id} {p.title}: "
                                  f"{len(structured['blocks'])} blocks")
            else:
                p.structured_content = structured
                p.save(update_fields=["structured_content", "updated_at"])
                count += 1

        if not options["dry_run"]:
            self.stdout.write(self.style.SUCCESS(f"Rebuilt metadata for {count} project(s)."))
