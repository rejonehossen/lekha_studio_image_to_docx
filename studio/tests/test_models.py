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

    def test_json_fields_default_empty(self):
        p = Project.objects.create(title="J")
        self.assertEqual(p.page_metadata, {})
        self.assertEqual(p.design_options, {})
        self.assertEqual(p.revision_history, [])
        self.assertEqual(p.export_history, [])

    def test_status_choices_include_all_spec_values(self):
        values = {k for k, _ in Project.STATUS_CHOICES}
        for v in ["draft", "uploaded", "processing", "review", "ready",
                  "exporting", "completed", "failed"]:
            self.assertIn(v, values)
