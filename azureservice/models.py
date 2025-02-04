from django.db import models
from user.models import Profile

class ImageUpload(models.Model):
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'imageUpload'

    def __str__(self):
        return f"Image {self.id} - {self.uploaded_at}"
