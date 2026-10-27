from django.test import SimpleTestCase
from studio.services import book_designer


class BookDesignTests(SimpleTestCase):
    def test_known_presets(self):
        for name in ["classic_literary", "modern_minimal", "academic_textbook", "clean_office"]:
            p = book_designer.get_preset(name)
            self.assertIn("page_format", p)
            self.assertIn("margins_mm", p)

    def test_fallback_preset(self):
        p = book_designer.get_preset("does-not-exist")
        self.assertEqual(p["page_format"], "A4")
