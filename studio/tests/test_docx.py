import tempfile
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
