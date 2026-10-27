import uuid
from pathlib import Path
from PIL import Image, UnidentifiedImageError
from django.conf import settings
from . import storage_service


class UploadError(Exception):
    pass


def validate_image(uploaded_file) -> dict:
    """
    Open the file with Pillow to validate real content (not filename trust).
    Returns metadata dict. Raises UploadError on failure.
    """
    if uploaded_file.size > settings.MAX_UPLOAD_BYTES:
        raise UploadError(
            f"File '{uploaded_file.name}' exceeds max size "
            f"({settings.MAX_UPLOAD_BYTES // (1024*1024)} MB)."
        )
    try:
        img = Image.open(uploaded_file)
        img.verify()
        uploaded_file.seek(0)
        img = Image.open(uploaded_file)
        fmt = (img.format or "").upper()
        if fmt not in settings.ALLOWED_IMAGE_FORMATS:
            raise UploadError(f"Unsupported image format: {fmt or 'unknown'}")
        width, height = img.size
        uploaded_file.seek(0)
        return {"format": fmt, "width": width, "height": height}
    except (UnidentifiedImageError, OSError) as e:
        raise UploadError(f"Cannot read image '{uploaded_file.name}': {e}")


def save_upload(project, uploaded_file) -> dict:
    """
    Validate + persist an uploaded image into the project's source dir.
    Returns a metadata dict appended to Project.source_images.
    """
    meta = validate_image(uploaded_file)
    ext = Path(uploaded_file.name).suffix.lower() or ".img"
    filename = f"{uuid.uuid4().hex}{ext}"
    dest = storage_service.source_dir(project.id) / filename
    with open(dest, "wb+") as f:
        for chunk in uploaded_file.chunks():
            f.write(chunk)
    return {
        "id": uuid.uuid4().hex,
        "original_name": Path(uploaded_file.name).name,
        "stored_path": storage_service.relative_to_media(dest),
        "bytes": dest.stat().st_size,
        "width": meta["width"],
        "height": meta["height"],
        "format": meta["format"],
        "order": 0,
    }
