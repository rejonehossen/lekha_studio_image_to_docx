"""
Image preprocessing module.

The current OCR pipeline feeds originals directly to the provider. This module
implements a small, honest subset of the preprocessing presets from the spec
using Pillow only (no OpenCV required). It preserves originals and writes
processed copies to media/projects/<id>/processed/.

Not implemented here (would need OpenCV): perspective correction, deskewing,
shadow removal, super-resolution, page-boundary detection. Those are
deliberately absent rather than faked.
"""
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance, ImageFilter

from . import storage_service


PRESETS = {
    "auto": {"contrast": 1.1, "sharpen": True, "grayscale": True},
    "handwriting": {"contrast": 1.25, "sharpen": True, "grayscale": True},
    "printed_book": {"contrast": 1.15, "sharpen": False, "grayscale": True},
    "scanned": {"contrast": 1.2, "sharpen": True, "grayscale": True},
    "low_light": {"contrast": 1.4, "sharpen": True, "grayscale": True},
    "high_contrast": {"contrast": 1.6, "sharpen": True, "grayscale": True},
}


def _apply(img: Image.Image, preset: dict) -> Image.Image:
    # EXIF orientation correction
    img = ImageOps.exif_transpose(img)
    if preset.get("grayscale"):
        img = img.convert("L")
    if preset.get("contrast"):
        img = ImageEnhance.Contrast(img).enhance(preset["contrast"])
    if preset.get("sharpen"):
        img = img.filter(ImageFilter.SHARPEN)
    return img


def preprocess_image(project, image_meta: dict, preset_name: str = "auto") -> dict:
    """
    Returns metadata for a processed copy (does not modify the original).
    """
    preset = PRESETS.get(preset_name, PRESETS["auto"])
    src = storage_service.resolve_media_relative(image_meta["stored_path"])
    out_dir = storage_service.processed_dir(project.id)
    out_path = out_dir / f"{image_meta['id']}_{preset_name}.png"

    with Image.open(src) as img:
        processed = _apply(img, preset)
        processed.save(out_path, format="PNG", optimize=True)

    return {
        "source_id": image_meta["id"],
        "preset": preset_name,
        "stored_path": storage_service.relative_to_media(out_path),
        "bytes": out_path.stat().st_size,
    }
