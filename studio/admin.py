from django.contrib import admin
from .models import Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at")
    search_fields = ("title", "extracted_text", "edited_text")
    readonly_fields = ("id", "created_at", "updated_at", "completed_at")
