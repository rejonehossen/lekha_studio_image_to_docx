"""
Book design presets and translation to python-docx layout parameters.
Only real, supported options are applied. Unsupported ones are documented.
"""

PAGE_FORMATS_MM = {
    "A4": (210, 297),
    "A5": (148, 210),
    "A6": (105, 148),
    "B5": (176, 250),
    "US Letter": (215.9, 279.4),
    "US Trade": (152.4, 228.6),
    "6x9": (152.4, 228.6),
    "5.5x8.5": (139.7, 215.9),
}

PRESETS = {
    "classic_literary": {
        "label": "Classic Literary Book",
        "page_format": "A5",
        "margins_mm": {"top": 20, "bottom": 20, "left": 18, "right": 18},
        "body_font": "Noto Serif Bengali",
        "body_size_pt": 11,
        "line_spacing": 1.4,
        "first_line_indent_mm": 6,
    },
    "modern_minimal": {
        "label": "Modern Minimalist",
        "page_format": "A5",
        "margins_mm": {"top": 22, "bottom": 22, "left": 22, "right": 22},
        "body_font": "Noto Sans Bengali",
        "body_size_pt": 10.5,
        "line_spacing": 1.35,
        "first_line_indent_mm": 0,
    },
    "academic_textbook": {
        "label": "Academic Textbook",
        "page_format": "A4",
        "margins_mm": {"top": 25, "bottom": 25, "left": 25, "right": 25},
        "body_font": "Noto Serif Bengali",
        "body_size_pt": 11,
        "line_spacing": 1.3,
        "first_line_indent_mm": 0,
    },
    "clean_office": {
        "label": "Clean Office Document",
        "page_format": "A4",
        "margins_mm": {"top": 20, "bottom": 20, "left": 20, "right": 20},
        "body_font": "Noto Sans Bengali",
        "body_size_pt": 11,
        "line_spacing": 1.15,
        "first_line_indent_mm": 0,
    },
}


def get_preset(name: str) -> dict:
    return PRESETS.get(name, PRESETS["clean_office"])


def page_size_mm(preset: dict) -> tuple:
    return PAGE_FORMATS_MM.get(preset["page_format"], PAGE_FORMATS_MM["A4"])


def mm_to_inches(mm: float) -> float:
    return mm / 25.4
