from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from studio.models import Project
from studio.services import upload_service


def make_image_bytes(fmt="PNG", size=(50, 50)):
    buf = BytesIO()
    Image.new("RGB", size, "white").save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


class UploadServiceTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Up")

    def test_valid_png_upload(self):
        f = SimpleUploadedFile("x.png", make_image_bytes("PNG"), content_type="image/png")
        meta = upload_service.save_upload(self.project, f)
        self.assertEqual(meta["format"], "PNG")
        self.assertEqual(meta["width"], 50)
        self.assertTrue(meta["stored_path"])
        self.assertTrue(meta["stored_path"].startswith("projects/"))

    def test_valid_jpeg_upload(self):
        f = SimpleUploadedFile("x.jpg", make_image_bytes("JPEG"), content_type="image/jpeg")
        meta = upload_service.save_upload(self.project, f)
        self.assertEqual(meta["format"], "JPEG")

    def test_invalid_content_rejected(self):
        f = SimpleUploadedFile("bad.png", b"not an image", content_type="image/png")
        with self.assertRaises(upload_service.UploadError):
            upload_service.save_upload(self.project, f)

    def test_oversized_rejected(self):
        from django.conf import settings
        from unittest import mock
        with mock.patch.object(settings, "MAX_UPLOAD_BYTES", 10):
            f = SimpleUploadedFile("big.png", make_image_bytes("PNG"), content_type="image/png")
            with self.assertRaises(upload_service.UploadError):
                upload_service.save_upload(self.project, f)


class UploadViewTests(TestCase):
    def test_upload_post_creates_image_metadata(self):
        p = Project.objects.create(title="V")
        f = SimpleUploadedFile("x.png", make_image_bytes("PNG"), content_type="image/png")
        r = self.client.post(reverse("studio:upload", args=[p.id]), {"images": f})
        self.assertIn(r.status_code, (302, 200))
        p.refresh_from_db()
        self.assertEqual(len(p.source_images), 1)
        self.assertEqual(p.status, "uploaded")
