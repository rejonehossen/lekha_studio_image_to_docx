import re


def to_structured(text: str) -> dict:
    """
    Very lightweight structuring: split into paragraphs.
    Detects likely headings (short lines, no terminal punctuation).
    """
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    blocks = []
    for p in paragraphs:
        first = p.split("\n")[0]
        is_heading = (
            len(first) < 80
            and not first.endswith((".", "?", "!", "।"))
            and len(p.split()) <= 12
        )
        blocks.append({"type": "heading" if is_heading else "paragraph", "text": p})
    return {"blocks": blocks}
