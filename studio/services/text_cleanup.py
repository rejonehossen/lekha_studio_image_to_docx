import re


def clean_ocr_text(text: str) -> str:
    """
    Conservative cleanup that preserves Bangla Unicode (Bengali block U+0980–U+09FF)
    and English. Does not attempt AI rewriting.
    """
    if not text:
        return ""
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Collapse 3+ blank lines to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    # Trim trailing whitespace per line
    text = "\n".join(line.rstrip() for line in text.split("\n"))
    # Repair hyphenated line-breaks: "exam-\nple" -> "example"
    text = re.sub(r"([A-Za-z])-\n([a-z])", r"\1\2", text)
    # Remove standalone page numbers on their own line
    text = re.sub(r"\n\s*\d{1,4}\s*\n", "\n", text)
    # Collapse single newlines within a paragraph into spaces IF safe:
    # only do this for adjacent lines that don't end in sentence punctuation
    lines = text.split("\n")
    out = []
    buf = ""
    for line in lines:
        if not line.strip():
            if buf:
                out.append(buf.rstrip())
                buf = ""
            out.append("")
            continue
        if buf and not buf.rstrip().endswith((".", "?", "!", "।", ":", ";")):
            buf += " " + line.strip()
        else:
            if buf:
                out.append(buf.rstrip())
            buf = line.strip()
    if buf:
        out.append(buf.rstrip())
    return "\n".join(out).strip()
