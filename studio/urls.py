from django.urls import path
from . import views

app_name = "studio"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("projects/new/", views.project_create, name="project_create"),
    path("projects/<uuid:project_id>/", views.project_detail, name="project_detail"),
    path("projects/<uuid:project_id>/upload/", views.upload, name="upload"),
    path("projects/<uuid:project_id>/process/", views.process, name="process"),
    path("projects/<uuid:project_id>/editor/", views.editor, name="editor"),
    path("projects/<uuid:project_id>/design/", views.book_designer, name="book_designer"),
    path("projects/<uuid:project_id>/export/", views.export, name="export"),
    path("projects/<uuid:project_id>/download/<str:filename>/", views.download, name="download"),
    path("projects/<uuid:project_id>/duplicate/", views.duplicate, name="duplicate"),
    path("projects/<uuid:project_id>/delete/", views.delete, name="delete"),
    path("settings/", views.settings_view, name="settings"),
]
