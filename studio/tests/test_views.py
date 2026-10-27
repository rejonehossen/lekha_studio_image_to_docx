from django.test import TestCase
from django.urls import reverse
from studio.models import Project


class ViewTests(TestCase):
    def test_dashboard_loads(self):
        r = self.client.get(reverse("studio:dashboard"))
        self.assertEqual(r.status_code, 200)

    def test_help_about(self):
        self.assertEqual(self.client.get(reverse("studio:help")).status_code, 200)
        self.assertEqual(self.client.get(reverse("studio:about")).status_code, 200)

    def test_create_and_open(self):
        r = self.client.post(reverse("studio:project_create"),
                             {"title": "Hello", "description": ""})
        self.assertEqual(r.status_code, 302)
        p = Project.objects.first()
        self.assertIsNotNone(p)
        r2 = self.client.get(reverse("studio:project_detail", args=[p.id]))
        self.assertEqual(r2.status_code, 200)

    def test_upload_requires_csrf(self):
        p = Project.objects.create(title="X")
        r = self.client.post(reverse("studio:upload", args=[p.id]), {})
        self.assertEqual(r.status_code, 403)

    def test_delete_project(self):
        p = Project.objects.create(title="Del")
        r = self.client.post(reverse("studio:delete", args=[p.id]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Project.objects.count(), 0)

    def test_editor_save(self):
        p = Project.objects.create(title="E")
        r = self.client.post(reverse("studio:editor", args=[p.id]),
                             {"action": "save", "text": "Hello"})
        self.assertEqual(r.status_code, 302)
        p.refresh_from_db()
        self.assertEqual(p.edited_text, "Hello")

    def test_preview_and_processing_pages(self):
        p = Project.objects.create(title="P")
        self.assertEqual(
            self.client.get(reverse("studio:preview", args=[p.id])).status_code, 200
        )
        self.assertEqual(
            self.client.get(reverse("studio:processing", args=[p.id])).status_code, 200
        )
