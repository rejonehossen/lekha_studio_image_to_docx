from django.utils import timezone
from . import storage_service, ocr_providers


def run_ocr(project, language_mode: str = "auto", provider_name: str = "tesseract"):
    """
    Recognize every source image in order and save results into the project.
    Updates project.status and project.extracted_text.
    Returns dict summary.
    """
    provider = ocr_providers.get_provider(provider_name)
    if not provider.is_available():
        project.status = "failed"
        project.error_message = "OCR provider unavailable (see settings diagnostics)."
        project.save(update_fields=["status", "error_message", "updated_at"])
        return {"ok": False, "error": project.error_message}

    pages = []
    combined = []
    for i, img_meta in enumerate(project.source_images):
        try:
            img_path = storage_service.resolve_media_relative(img_meta["stored_path"])
        except ValueError:
            continue
        result = provider.recognize(img_path, mode=language_mode)
        pages.append({
            "order": i,
            "source_id": img_meta.get("id"),
            "engine": result.engine,
            "lang": result.lang,
            "text": result.text,
            "error": result.error,
        })
        if result.text:
            combined.append(result.text)

    project.extracted_text = "\n\n".join(combined).strip()
    project.page_metadata = {**(project.page_metadata or {}), "ocr": pages}
    project.status = "review" if project.extracted_text else "failed"
    if not project.extracted_text:
        project.error_message = "OCR produced no text."
    else:
        project.error_message = ""
    project.save(update_fields=[
        "extracted_text", "page_metadata", "status", "error_message", "updated_at"
    ])
    return {"ok": bool(project.extracted_text), "pages": len(pages)}
