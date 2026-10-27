import uuid
from django.db import models


class Project(models.Model):
    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("uploaded", "Uploaded"),
        ("processing", "Processing"),
        ("review", "Review"),
        ("ready", "Ready"),
        ("exporting", "Exporting"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True, null=True, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default="draft", db_index=True)

    # File metadata (paths relative to MEDIA_ROOT), never binaries in DB
    source_images = models.JSONField(default=list, blank=True)
    extracted_text = models.TextField(blank=True)
    edited_text = models.TextField(blank=True)

    structured_content = models.JSONField(default=dict, blank=True)
    page_metadata = models.JSONField(default=dict, blank=True)
    processing_options = models.JSONField(default=dict, blank=True)
    design_options = models.JSONField(default=dict, blank=True)
    revision_history = models.JSONField(default=list, blank=True)
    export_history = models.JSONField(default=list, blank=True)
    project_settings = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_opened_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    class Meta:
        ordering = ["-updated_at"]
        indexes = [models.Index(fields=["status", "-updated_at"])]

    def __str__(self):
        return self.title
