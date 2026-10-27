# Book Design

Presets are defined in `studio/services/book_designer.py`. Each preset controls:

- Page format (A4, A5, A6, B5, US Letter, US Trade, 6×9, 5.5×8.5)
- Margins (mm)
- Body font name (must be installed on the machine opening the file)
- Body font size (pt)
- Line spacing (multiple)
- First-line indent (mm)

## Adding a preset

```python
PRESETS["my_preset"] = {
    "label": "My Preset",
    "page_format": "B5",
    "margins_mm": {"top": 20, "bottom": 20, "left": 20, "right": 20},
    "body_font": "Kalpurush",
    "body_size_pt": 11,
    "line_spacing": 1.35,
    "first_line_indent_mm": 5,
}
