from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from studio.models import Project


class ViewTests(TestCase):
    def test_dashboard_loads(self):
        r = self.client.get(reverse("studio:dashboard"))
        self.assertEqual(r.status_code, 200)

    def test_create_and_open(self):
        r = self.client.post(reverse("studio:project_create"), {"title": "Hello", "description": ""})
        self.assertEqual(r.status_code, 302)
        p = Project.objects.first()
        self.assertIsNotNone(p)
        r2 = self.client.get(reverse("studio:project_detail", args=[p.id]))
        self.assertEqual(r2.status_code, 200)

    def test_upload_requires_csrf(self):
        p = Project.objects.create(title="X")
        # Missing CSRF token → 403
        r = self.client.post(reverse("studio:upload", args=[p.id]), {})
        self.assertEqual(r.status_code, 403)

    def test_delete_project(self):
        p = Project.objects.create(title="Del")
        r = self.client.post(reverse("studio:delete", args=[p.id]))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Project.objects.count(), 0)
