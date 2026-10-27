from io import BytesIO
from PIL import Image
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from studio.models import Project
from studio.services import upload_service


def make_image_bytes(fmt="PNG", size=(50, 50)):
    buf = BytesIO()
    Image.new("RGB", size, "white").save(buf, format=fmt)
    buf.seek(0)
    return buf.read()


class UploadTests(TestCase):
    def setUp(self):
        self.project = Project.objects.create(title="Up")

    def test_valid_png_upload(self):
        f = SimpleUploadedFile("x.png", make_image_bytes("PNG"), content_type="image/png")
        meta = upload_service.save_upload(self.project, f)
        self.assertEqual(meta["format"], "PNG")
        self.assertEqual(meta["width"], 50)

    def test_invalid_content_rejected(self):
        f = SimpleUploadedFile("bad.png", b"not an image", content_type="image/png")
        with self.assertRaises(upload_service.UploadError):
            upload_service.save_upload(self.project, f)
