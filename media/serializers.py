from rest_framework import serializers
from .models import ImageUpload


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageUpload
        fields = ['id', 'image_name', 'image_url', 'thumbnail_url', 'uploaded_at']
        read_only_fields = ['id', 'image_url', 'thumbnail_url', 'uploaded_at']
