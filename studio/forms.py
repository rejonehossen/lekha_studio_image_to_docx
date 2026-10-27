from django import forms
from .models import Project


class ProjectCreateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "description"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "input", "placeholder": "e.g. আমার প্রথম উপন্যাস"}),
            "description": forms.Textarea(attrs={"class": "input", "rows": 3}),
        }


class ImageUploadForm(forms.Form):
    images = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True, "class": "input"}),
        required=True,
    )

    def clean_images(self):
        files = self.files.getlist("images")
        if not files:
            raise forms.ValidationError("No files selected.")
        return files


class EditorForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=False)


class LanguageForm(forms.Form):
    LANGUAGE_CHOICES = [
        ("auto", "Auto"),
        ("bangla", "Bangla only"),
        ("english", "English only"),
        ("mixed", "Mixed Bangla-English"),
    ]
    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, initial="auto")


class DesignForm(forms.Form):
    PRESET_CHOICES = [
        ("classic_literary", "Classic Literary Book"),
        ("modern_minimal", "Modern Minimalist"),
        ("academic_textbook", "Academic Textbook"),
        ("clean_office", "Clean Office Document"),
    ]
    preset = forms.ChoiceField(choices=PRESET_CHOICES, initial="clean_office")
