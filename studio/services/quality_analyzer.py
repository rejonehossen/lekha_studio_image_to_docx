"""Preflight quality checks on a project before export."""


def analyze(project) -> dict:
    warnings = []
    text = project.edited_text or project.extracted_text or ""

    if not text.strip():
        warnings.append("Document has no text.")
    elif len(text.strip()) < 40:
        warnings.append("Very little text — check OCR results.")

    if project.source_images and not (project.page_metadata or {}).get("ocr"):
        warnings.append("Images are uploaded but OCR has not been run.")

    if not project.design_options or "preset" not in (project.design_options or {}):
        warnings.append("No book design preset selected; default 'clean_office' will be used.")

    # Simple duplicate-line detection
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    seen = set()
    dups = 0
    for ln in lines:
        if len(ln) < 12:
            continue
        if ln in seen:
            dups += 1
        seen.add(ln)
    if dups >= 5:
        warnings.append(f"{dups} repeated lines detected — possible duplicated page.")

    return {"ok": not warnings, "warnings": warnings}






















