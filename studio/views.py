from django.conf import settings
from django.contrib import messages
from django.db import transaction
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .models import Project
from . import forms
from .services import (
    project_service, upload_service, ocr_service, export_service,
    storage_service, settings_service, text_cleanup,
)


def dashboard(request):
    qs = Project.objects.all()
    q = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    sort = request.GET.get("sort", "-updated_at")
    if q:
        qs = qs.filter(title__icontains=q) | qs.filter(extracted_text__icontains=q)
    if status:
        qs = qs.filter(status=status)
    allowed_sorts = {"-updated_at", "updated_at", "-created_at", "created_at", "title", "-title"}
    if sort not in allowed_sorts:
        sort = "-updated_at"
    qs = qs.order_by(sort)
    ctx = {
        "projects": qs[:100],
        "q": q, "status": status, "sort": sort,
        "statuses": Project.STATUS_CHOICES,
        "total": Project.objects.count(),
        "in_progress": Project.objects.filter(status__in=["uploaded", "processing", "review", "ready"]).count(),
        "completed": Project.objects.filter(status="completed").count(),
    }
    return render(request, "studio/dashboard.html", ctx)


@require_http_methods(["GET", "POST"])
def project_create(request):
    if request.method == "POST":
        form = forms.ProjectCreateForm(request.POST)
        if form.is_valid():
            p = form.save()
            return redirect("studio:project_detail", project_id=p.id)
    else:
        form = forms.ProjectCreateForm()
    return render(request, "studio/project_create.html", {"form": form})


def project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    Project.objects.filter(pk=project.pk).update(last_opened_at=timezone.now())
    return render(request, "studio/project_detail.html", {"project": project})


@require_http_methods(["GET", "POST"])
def upload(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    errors = []
    if request.method == "POST":
        files = request.FILES.getlist("images")
        if not files:
            errors.append("No files selected.")
        if len(project.source_images or []) + len(files) > settings.MAX_BATCH_IMAGES:
            errors.append(f"Batch limit is {settings.MAX_BATCH_IMAGES} images.")
        new_meta = []
        for f in files:
            try:
                new_meta.append(upload_service.save_upload(project, f))
            except upload_service.UploadError as e:
                errors.append(str(e))
        if new_meta:
            existing = project.source_images or []
            for i, m in enumerate(new_meta):
                m["order"] = len(existing) + i
            project.source_images = existing + new_meta
            project.status = "uploaded"
            project.save(update_fields=["source_images", "status", "updated_at"])
            messages.success(request, f"Uploaded {len(new_meta)} image(s).")
        if not errors:
            return redirect("studio:upload", project_id=project.id)
    return render(request, "studio/upload.html", {"project": project, "errors": errors})


@require_POST
def process(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    language = request.POST.get("language", "auto")
    result = ocr_service.run_ocr(project, language_mode=language)
    if result.get("ok"):
        messages.success(request, "OCR completed. Review the text below.")
        return redirect("studio:editor", project_id=project.id)
    messages.error(request, result.get("error", "OCR failed."))
    return redirect("studio:project_detail", project_id=project.id)


@require_http_methods(["GET", "POST"])
def editor(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        action = request.POST.get("action", "save")
        text = request.POST.get("text", "")
        if action == "save":
            project_service.save_text(project, text)
            messages.success(request, "Saved.")
        elif action == "clean":
            cleaned = text_cleanup.clean_ocr_text(text)
            project_service.save_text(project, cleaned)
            messages.success(request, "Cleaned text applied.")
        return redirect("studio:editor", project_id=project.id)
    # If editor blank but extracted text exists, prefill edited_text
    if not project.edited_text and project.extracted_text:
        project.edited_text = project.extracted_text
        project.structured_content = project_service.text_organizer.to_structured(project.edited_text)
        project.save(update_fields=["edited_text", "structured_content", "updated_at"])
    return render(request, "studio/editor.html", {"project": project})


@require_http_methods(["GET", "POST"])
def book_designer(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        form = forms.DesignForm(request.POST)
        if form.is_valid():
            opts = dict(project.design_options or {})
            opts["preset"] = form.cleaned_data["preset"]
            project.design_options = opts
            project.save(update_fields=["design_options", "updated_at"])
            messages.success(request, "Design updated.")
            return redirect("studio:book_designer", project_id=project.id)
    else:
        form = forms.DesignForm(initial={"preset": (project.design_options or {}).get("preset", "clean_office")})
    return render(request, "studio/book_designer.html", {"project": project, "form": form})


@require_POST
def export(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    try:
        entry = export_service.export_docx(project)
    except Exception as e:
        messages.error(request, f"Export failed: {e}")
        return redirect("studio:project_detail", project_id=project.id)
    messages.success(request, "DOCX generated.")
    return redirect("studio:download", project_id=project.id, filename=entry["filename"])


def download(request, project_id, filename):
    project = get_object_or_404(Project, pk=project_id)
    # Only allow filenames that exist in export history
    allowed = {e["filename"] for e in (project.export_history or [])}
    if filename not in allowed:
        raise Http404("Export not found.")
    path = storage_service.resolve_media_relative(
        next(e["relative_path"] for e in project.export_history if e["filename"] == filename)
    )
    if not path.exists():
        raise Http404("File missing on disk.")
    return FileResponse(open(path, "rb"), as_attachment=True, filename=filename)


@require_POST
def duplicate(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    new = project_service.duplicate_project(project)
    messages.success(request, "Project duplicated.")
    return redirect("studio:project_detail", project_id=new.id)


@require_POST
def delete(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project.delete()
    messages.success(request, "Project deleted.")
    return redirect("studio:dashboard")


def settings_view(request):
    from django.conf import settings as dj_settings
    from .services import settings_service
    ctx = {
        "ocr": settings_service.ocr_diagnostics(),
        "fonts_hint": settings_service.known_fonts_hint(),
        "storage": settings_service.storage_info(dj_settings.MEDIA_ROOT),
        "max_upload_mb": dj_settings.MAX_UPLOAD_BYTES // (1024 * 1024),
        "max_batch": dj_settings.MAX_BATCH_IMAGES,
    }
    return render(request, "studio/settings.html", ctx)





def help_view(request):
    return render(request, "studio/help.html")


def about_view(request):
    return render(request, "studio/about.html")


def processing(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "studio/processing.html", {"project": project})


def preview(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return render(request, "studio/document_preview.html", {"project": project})
