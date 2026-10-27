from django.test import TestCase, SimpleTestCase
from studio.services import ocr_providers
from studio.services.language_service import detect_script


class ProviderTests(TestCase):
    def test_unknown_provider_raises(self):
        with self.assertRaises(ocr_providers.ProviderUnavailable):
            ocr_providers.get_provider("does-not-exist")

    def test_tesseract_availability_is_boolean(self):
        p = ocr_providers.TesseractProvider()
        self.assertIsInstance(p.is_available(), bool)


class ScriptDetectionTests(SimpleTestCase):
    def test_bangla(self):
        self.assertEqual(detect_script("বাংলা লেখা"), "bangla")

    def test_english(self):
        self.assertEqual(detect_script("English text"), "english")

    def test_mixed(self):
        self.assertEqual(detect_script("Bangla বাংলা"), "mixed")

    def test_empty(self):
        self.assertEqual(detect_script(""), "empty")
