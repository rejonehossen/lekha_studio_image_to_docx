"""
Typography helpers. Font *names* are written into OOXML; the font file is not
embedded. Correct rendering requires the font to be installed wherever the
document is opened.
"""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_complex_script_font(run, font_name: str):
    """Set Latin + complex-script (Bangla) fonts on a run."""
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:ascii"), font_name)
    rFonts.set(qn("w:hAnsi"), font_name)
    rFonts.set(qn("w:cs"), font_name)
    rFonts.set(qn("w:eastAsia"), font_name)


def set_style_complex_script_font(style, font_name: str):
    """Set complex-script font on a paragraph style."""
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    rFonts.set(qn("w:cs"), font_name)
    rFonts.set(qn("w:eastAsia"), font_name)
