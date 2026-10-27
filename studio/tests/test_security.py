from pathlib import Path
from django.test import SimpleTestCase
from django.conf import settings
from studio.services.storage_service import resolve_media_relative, project_dir

class PathTraversalTests(SimpleTestCase):
    def test_rejects_traversal(self):
        with self.assertRaises(ValueError):
            resolve_media_relative("../../etc/passwd")

    def test_rejects_absolute_escape(self):
        with self.assertRaises(ValueError):
            resolve_media_relative("/etc/passwd")

    def test_accepts_normal(self):
        p = resolve_media_relative("projects/some/uuid/file.png")
        self.assertTrue(str(p).startswith(str(Path(settings.MEDIA_ROOT).resolve())))

    def test_project_dir_uuid_sanitized(self):
        # Non-UUID input must be rejected by uuid.UUID()
        with self.assertRaises(ValueError):
            project_dir("../../../evil")
