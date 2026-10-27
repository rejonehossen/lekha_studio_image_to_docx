from django.test import SimpleTestCase
from studio.services import book_designer


class BookDesignTests(SimpleTestCase):
    def test_known_presets_have_required_keys(self):
        for name in ["classic_literary", "modern_minimal",
                     "academic_textbook", "clean_office"]:
            p = book_designer.get_preset(name)
            for key in ["page_format", "margins_mm", "body_font",
                        "body_size_pt", "line_spacing", "first_line_indent_mm"]:
                self.assertIn(key, p)

    def test_fallback_preset(self):
        p = book_designer.get_preset("does-not-exist")
        self.assertEqual(p["page_format"], "A4")

    def test_page_size_conversion(self):
        p = book_designer.get_preset("classic_literary")
        w, h = book_designer.page_size_mm(p)
        self.assertAlmostEqual(w, 148.0)
        self.assertAlmostEqual(h, 210.0)

    def test_mm_to_inches(self):
        self.assertAlmostEqual(book_designer.mm_to_inches(25.4), 1.0)
