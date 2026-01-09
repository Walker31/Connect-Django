from django.db import models
from django.contrib.auth.models import User


class ImageUpload(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    image_name = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.URLField(max_length=2048, null=True, blank=True)  # Cloudinary URL
    thumbnail_url = models.URLField(max_length=2048, null=True, blank=True)  # Cloudinary thumbnail URL
    public_id = models.CharField(max_length=255, null=True, blank=True)  # Cloudinary public_id for deletion
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image_upload'

    def __str__(self):
        return f"{self.user.username if self.user else 'Anonymous'} - {self.image_name}"
