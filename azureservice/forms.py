# forms.py
from django import forms
from .models import ImageUpload

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = ImageUpload
        fields = ['image']  # Use 'image' instead of 'file'
