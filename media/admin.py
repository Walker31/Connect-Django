from django.contrib import admin
from .models import ImageUpload


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ['user', 'image_name', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['user__username', 'image_name']
