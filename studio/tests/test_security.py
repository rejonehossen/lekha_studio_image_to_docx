from pathlib import Path
from django.test import SimpleTestCase, override_settings
from django.conf import settings
from studio.services.storage_service import resolve_media_relative


class PathTraversalTests(SimpleTestCase):
    def test_rejects_traversal(self):
        with self.assertRaises(ValueError):
            resolve_media_relative("../../etc/passwd")

    def test_accepts_normal(self):
        p = resolve_media_relative("projects/some/uuid/file.png")
        self.assertTrue(str(p).startswith(str(Path(settings.MEDIA_ROOT).resolve())))
