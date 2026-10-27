"""
Build a real, editable DOCX from project structured content + design preset.
Uses python-docx. Genuine Word styles, page size, margins, section breaks,
header/footer with page-number field, and heading styles.
"""
from pathlib import Path
from docx import Document
from docx.shared import Pt, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

from . import book_designer


def _set_complex_script_font(run, font_name: str):
    """Set east-Asian / complex-script font so Bangla renders with the chosen font."""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:cs"), font_name)
    rFonts.set(qn("w:eastAsia"), font_name)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)


def _add_page_number_footer(section, font_name: str):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    _set_complex_script_font(run, font_name)
    # Insert field: PAGE
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run._r.append(fld_begin)
    run._r.append(instr)
    run._r.append(fld_end)


def build_docx(project, output_path: Path) -> Path:
    preset_name = (project.design_options or {}).get("preset", "clean_office")
    preset = book_designer.get_preset(preset_name)
    page_w_mm, page_h_mm = book_designer.page_size_mm(preset)

    doc = Document()

    # Page setup
    section = doc.sections[0]
    section.page_width = Mm(page_w_mm)
    section.page_height = Mm(page_h_mm)
    m = preset["margins_mm"]
    section.top_margin = Mm(m["top"])
    section.bottom_margin = Mm(m["bottom"])
    section.left_margin = Mm(m["left"])
    section.right_margin = Mm(m["right"])

    # Base styles
    normal = doc.styles["Normal"]
    normal.font.name = preset["body_font"]
    normal.font.size = Pt(preset["body_size_pt"])
    # Complex-script font on style
    rpr = normal.element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:cs"), preset["body_font"])

    # Title page
    title_par = doc.add_paragraph()
    title_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_run = title_par.add_run(project.title)
    title_run.bold = True
    title_run.font.size = Pt(24)
    _set_complex_script_font(title_run, preset["body_font"])

    doc.add_page_break()

    # Content
    structured = project.structured_content or {}
    blocks = structured.get("blocks") or []
    if not blocks:
        # fall back to edited_text
        for para in (project.edited_text or "").split("\n\n"):
            para = para.strip()
            if not para:
                continue
            p = doc.add_paragraph(para)
            for run in p.runs:
                _set_complex_script_font(run, preset["body_font"])
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.MULTIPLE
            p.paragraph_format.line_spacing = preset["line_spacing"]
    else:
        for block in blocks:
            text = block.get("text", "")
            if not text:
                continue
            if block.get("type") == "heading":
                h = doc.add_heading(level=1)
                run = h.add_run(text)
                _set_complex_script_font(run, preset["body_font"])
            else:
                p = doc.add_paragraph()
                run = p.add_run(text)
                _set_complex_script_font(run, preset["body_font"])
                p.paragraph_format.line_spacing = preset["line_spacing"]
                if preset.get("first_line_indent_mm"):
                    p.paragraph_format.first_line_indent = Mm(preset["first_line_indent_mm"])

    # Footer page numbers
    _add_page_number_footer(section, preset["body_font"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    return output_path
