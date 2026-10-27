from django.db import transaction
from django.utils import timezone
from ..models import Project
from . import text_organizer


def create_project(title: str, description: str = "") -> Project:
    return Project.objects.create(title=title[:255], description=description)


def save_text(project: Project, text: str, make_revision: bool = True):
    with transaction.atomic():
        if make_revision and project.edited_text != text:
            revs = project.revision_history or []
            revs.insert(0, {
                "at": timezone.now().isoformat(),
                "text": project.edited_text,
            })
            project.revision_history = revs[:50]
        project.edited_text = text
        project.structured_content = text_organizer.to_structured(text)
        project.save(update_fields=[
            "edited_text", "structured_content", "revision_history", "updated_at"
        ])


def duplicate_project(project: Project) -> Project:
    new = Project.objects.create(
        title=f"{project.title} (copy)",
        description=project.description,
        source_images=list(project.source_images or []),
        extracted_text=project.extracted_text,
        edited_text=project.edited_text,
        structured_content=dict(project.structured_content or {}),
        page_metadata=dict(project.page_metadata or {}),
        processing_options=dict(project.processing_options or {}),
        design_options=dict(project.design_options or {}),
        project_settings=dict(project.project_settings or {}),
        status="review",
    )
    return new
