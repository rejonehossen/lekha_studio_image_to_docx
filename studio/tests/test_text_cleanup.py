from django.test import SimpleTestCase
from studio.services.text_cleanup import clean_ocr_text


class CleanupTests(SimpleTestCase):
    def test_preserves_bangla_unicode(self):
        text = "বাংলা লেখা।\n\nদ্বিতীয় অনুচ্ছেদ।"
        self.assertEqual(clean_ocr_text(text), text.strip())

    def test_repairs_hyphenated_linebreaks(self):
        self.assertEqual(clean_ocr_text("exam-\nple"), "example")

    def test_collapses_blank_lines(self):
        self.assertEqual(clean_ocr_text("a\n\n\n\nb"), "a\n\nb")
