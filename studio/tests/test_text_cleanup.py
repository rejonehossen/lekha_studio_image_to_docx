from django.test import SimpleTestCase
from studio.services.text_cleanup import clean_ocr_text
from studio.services.text_organizer import to_structured


class CleanupTests(SimpleTestCase):
    def test_preserves_bangla_unicode(self):
        text = "বাংলা লেখা।\n\nদ্বিতীয় অনুচ্ছেদ।"
        self.assertEqual(clean_ocr_text(text), text.strip())

    def test_preserves_english(self):
        self.assertEqual(clean_ocr_text("Hello, world."), "Hello, world.")

    def test_mixed_language(self):
        text = "English এবং বাংলা mixed."
        self.assertEqual(clean_ocr_text(text), text.strip())

    def test_repairs_hyphenated_linebreaks(self):
        self.assertEqual(clean_ocr_text("exam-\nple"), "example")

    def test_collapses_blank_lines(self):
        self.assertEqual(clean_ocr_text("a\n\n\n\nb"), "a\n\nb")

    def test_strips_page_numbers(self):
        text = "Real content here.\n42\nMore content."
        self.assertNotIn("42", clean_ocr_text(text))

    def test_empty(self):
        self.assertEqual(clean_ocr_text(""), "")


class OrganizerTests(SimpleTestCase):
    def test_paragraph_split(self):
        s = to_structured("Para one.\n\nPara two.")
        types = [b["type"] for b in s["blocks"]]
        self.assertEqual(types, ["paragraph", "paragraph"])

    def test_heading_heuristic(self):
        s = to_structured("Chapter One\n\nBody text that is longer.")
        self.assertEqual(s["blocks"][0]["type"], "heading")

    def test_empty_input(self):
        self.assertEqual(to_structured(""), {"blocks": []})
