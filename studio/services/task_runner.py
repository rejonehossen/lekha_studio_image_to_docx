"""
Local synchronous task runner. Runs OCR in-process; used by the /process/ view.

A background worker / queue is intentionally NOT provided in this codebase.
If you need asynchronous processing, run a dedicated process that calls
ocr_service.run_ocr(project) — do not add Redis/Celery without also updating
DATABASES/SQLite concurrency settings.
"""


def run_synchronously(fn, *args, **kwargs):
    return fn(*args, **kwargs)

