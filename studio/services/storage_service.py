import uuid
from pathlib import Path
from django.conf import settings


def project_dir(project_id) -> Path:
    """Return a safe, per-project directory under MEDIA_ROOT/projects/<uuid>/."""
    safe_id = str(uuid.UUID(str(project_id)))
    d = Path(settings.MEDIA_ROOT) / "projects" / safe_id
    d.mkdir(parents=True, exist_ok=True)
    return d


def source_dir(project_id) -> Path:
    d = project_dir(project_id) / "source"
    d.mkdir(parents=True, exist_ok=True)
    return d


def processed_dir(project_id) -> Path:
    d = project_dir(project_id) / "processed"
    d.mkdir(parents=True, exist_ok=True)
    return d


def exports_dir(project_id) -> Path:
    d = project_dir(project_id) / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def relative_to_media(path: Path) -> str:
    return path.resolve().relative_to(Path(settings.MEDIA_ROOT).resolve()).as_posix()


def resolve_media_relative(rel_path: str) -> Path:
    """Resolve a stored relative path safely, rejecting traversal."""
    media_root = Path(settings.MEDIA_ROOT).resolve()
    target = (media_root / rel_path).resolve()
    if not str(target).startswith(str(media_root)):
        raise ValueError("Path escapes media root")
    return target
