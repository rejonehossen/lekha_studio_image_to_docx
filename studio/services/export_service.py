import uuid
import zipfile
from pathlib import Path
from django.utils import timezone
from . import storage_service, docx_builder


def validate_docx(path: Path) -> bool:
    """Validate ZIP container and required Word parts."""
    if not path.exists():
        return False
    try:
        with zipfile.ZipFile(path) as z:
            names = set(z.namelist())
            return "[Content_Types].xml" in names and "word/document.xml" in names
    except zipfile.BadZipFile:
        return False


def export_docx(project) -> dict:
    filename = f"{uuid.uuid4().hex}.docx"
    out_path = storage_service.exports_dir(project.id) / filename
    docx_builder.build_docx(project, out_path)
    if not validate_docx(out_path):
        raise RuntimeError("Generated DOCX failed structural validation.")
    entry = {
        "filename": filename,
        "relative_path": storage_service.relative_to_media(out_path),
        "bytes": out_path.stat().st_size,
        "created_at": timezone.now().isoformat(),
    }
    history = project.export_history or []
    history.insert(0, entry)
    project.export_history = history[:20]
    project.status = "completed"
    project.completed_at = timezone.now()
    project.save(update_fields=["export_history", "status", "completed_at", "updated_at"])
    return entry
