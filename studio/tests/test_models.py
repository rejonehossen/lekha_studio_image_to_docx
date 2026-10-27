from django.test import TestCase
from studio.models import Project


class ProjectModelTests(TestCase):
    def test_create_project_defaults(self):
        p = Project.objects.create(title="Test")
        self.assertEqual(p.status, "draft")
        self.assertEqual(p.source_images, [])
        self.assertIsNotNone(p.id)

    def test_uuid_primary_key(self):
        p = Project.objects.create(title="T")
        self.assertEqual(len(str(p.id)), 36)
