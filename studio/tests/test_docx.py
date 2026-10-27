import tempfile
import zipfile
from pathlib import Path
from django.test import TestCase
from studio.models import Project
from studio.services import docx_builder, export_service


class DocxTests(TestCase):
    def test_build_and_validate(self):
        p = Project.objects.create(
            title="আমার বই / My Book",
            edited_text="প্রথম অনুচ্ছেদ।\n\nSecond paragraph.",
            structured_content={"blocks": [
                {"type": "heading", "text": "Chapter 1"},
                {"type": "paragraph", "text": "প্রথম অনুচ্ছেদ।"},
                {"type": "paragraph", "text": "Second paragraph."},
            ]},
            design_options={"preset": "classic_literary"},
        )
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "test.docx"
            docx_builder.build_docx(p, out)
            self.assertTrue(out.exists())
            self.assertTrue(export_service.validate_docx(out))

    def test_docx_contains_required_parts(self):
        p = Project.objects.create(title="T", edited_text="hello")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "t.docx"
            docx_builder.build_docx(p, out)
            with zipfile.ZipFile(out) as z:
                names = set(z.namelist())
                self.assertIn("[Content_Types].xml", names)
                self.assertIn("word/document.xml", names)

    def test_bangla_preserved_in_docx(self):
        bangla = "বাংলা লেখা পরীক্ষা"
        p = Project.objects.create(title="B", edited_text=bangla,
                                   structured_content={"blocks": [
                                       {"type": "paragraph", "text": bangla},
                                   ]})
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "b.docx"
            docx_builder.build_docx(p, out)
            with zipfile.ZipFile(out) as z:
                xml = z.read("word/document.xml").decode("utf-8")
            # Bangla should appear as-is in the XML
            self.assertIn(bangla, xml)

    def test_validate_rejects_non_docx(self):
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.docx"
            bad.write_bytes(b"not a zip")
            self.assertFalse(export_service.validate_docx(bad))

    def test_export_service_updates_history(self):
        p = Project.objects.create(
            title="Export",
            edited_text="content",
            structured_content={"blocks": [
                {"type": "paragraph", "text": "content"},
            ]},
        )
        entry = export_service.export_docx(p)
        p.refresh_from_db()
        self.assertEqual(p.status, "completed")
        self.assertEqual(len(p.export_history), 1)
        self.assertEqual(p.export_history[0]["filename"], entry["filename"])
