"""Preflight quality checks on a project before export."""


def analyze(project) -> dict:
    warnings = []
    text = project.edited_text or project.extracted_text or ""
    if not text.strip():
        warnings.append("Document has no text.")
    if len(text) < 40:
        warnings.append("Very little text — check OCR results.")
    if not project.design_options or "preset" not in (project.design_options or {}):
        warnings.append("No book design preset selected; default Clean Office will be used.")
    if project.source_images and not (project.page_metadata or {}).get("ocr"):
        warnings.append("Images uploaded but OCR has not been run.")
    return {"ok": not warnings, "warnings": warnings}
