from django.test import TestCase
from studio.services import ocr_providers


class ProviderTests(TestCase):
    def test_unknown_provider_raises(self):
        with self.assertRaises(ocr_providers.ProviderUnavailable):
            ocr_providers.get_provider("does-not-exist")

    def test_tesseract_availability_is_boolean(self):
        p = ocr_providers.TesseractProvider()
        self.assertIsInstance(p.is_available(), bool)

    def test_lang_string_english_or_raises(self):
        p = ocr_providers.TesseractProvider()
        if not p.is_available():
            self.skipTest("Tesseract not installed in this environment.")
        # English lang may or may not be installed; assert either result or raise path
        try:
            langs = p.lang_string("english")
            self.assertIn("eng", langs)
        except ocr_providers.ProviderUnavailable:
            pass
