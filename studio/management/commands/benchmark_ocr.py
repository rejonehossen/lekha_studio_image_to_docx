"""
Run OCR over a folder of images with ground-truth .txt sidecars and compute
character error rate (CER) and word error rate (WER). Honest: prints real
numbers; refuses to fabricate when tesseract is unavailable.

Usage:
    python manage.py benchmark_ocr --folder samples/ --language english
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from studio.services.ocr_providers import TesseractProvider


def _levenshtein(a, b):
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(
                prev[j] + 1,
                cur[j - 1] + 1,
                prev[j - 1] + (ca != cb),
            ))
        prev = cur
    return prev[-1]


def cer(ref, hyp):
    if not ref:
        return 0.0 if not hyp else 1.0
    return _levenshtein(ref, hyp) / len(ref)


def wer(ref, hyp):
    ref_w = ref.split()
    hyp_w = hyp.split()
    if not ref_w:
        return 0.0 if not hyp_w else 1.0
    return _levenshtein(ref_w, hyp_w) / len(ref_w)


class Command(BaseCommand):
    help = "Benchmark OCR against ground-truth .txt sidecars. Real CER/WER only."

    def add_arguments(self, parser):
        parser.add_argument("--folder", required=True)
        parser.add_argument("--language", default="english")
        parser.add_argument("--provider", default="tesseract")

    def handle(self, *args, **options):
        folder = Path(options["folder"])
        if not folder.is_dir():
            raise CommandError(f"Folder not found: {folder}")

        provider = TesseractProvider()
        if not provider.is_available():
            raise CommandError("Tesseract is not installed. Cannot benchmark.")

        images = sorted([p for p in folder.iterdir()
                         if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")])
        if not images:
            raise CommandError("No images found.")

        total_c = 0.0
        total_w = 0.0
        n = 0
        for img in images:
            ref_file = img.with_suffix(".txt")
            if not ref_file.exists():
                self.stdout.write(self.style.WARNING(f"Skip {img.name}: no ground truth."))
                continue
            ref = ref_file.read_text(encoding="utf-8")
            result = provider.recognize(str(img), mode=options["language"])
            if result.error:
                self.stdout.write(self.style.ERROR(f"{img.name}: {result.error}"))
                continue
            c = cer(ref, result.text)
            w = wer(ref, result.text)
            total_c += c
            total_w += w
            n += 1
            self.stdout.write(f"{img.name}: CER={c:.4f} WER={w:.4f}")

        if n:
            self.stdout.write(self.style.SUCCESS(
                f"\nAveraged over {n} sample(s): "
                f"CER={total_c/n:.4f} WER={total_w/n:.4f}"
            ))
        else:
            self.stdout.write(self.style.ERROR("No samples evaluated."))
