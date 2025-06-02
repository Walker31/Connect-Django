from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from .models import ImageUpload
from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import FileUploadForm
import logging
from .utils import generate_thumbnail

logger = logging.getLogger(__name__)

class IndexView(LoginRequiredMixin, View):
    def get(self, request):
        form = FileUploadForm()
        return render(request, 'index.html', {'form': form})

    def post(self, request):
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.profile = request.user
            upload.save()
            return redirect('/')
        return render(request, 'index.html', {'form': form})
    
class UploadImageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        images = request.FILES.getlist('images')
        uploaded_data = []

        if not images:
            return Response({"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        if len(images) > 6:
            return Response({"detail": "You can upload a maximum of 5 images at a time."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)

            for image in images:
                blob_client = container_client.get_blob_client(image.name)
                blob_client.upload_blob(image, overwrite=True)

                thumbnail_content = generate_thumbnail(image)
                thumb_blob_name = f"thumbs/thumb_{image.name}"
                thumb_blob_client = container_client.get_blob_client(thumb_blob_name)
                thumb_blob_client.upload_blob(thumbnail_content, overwrite=True)

                image_url = blob_client.url
                thumbnail_url = thumb_blob_client.url

                ImageUpload.objects.create(
                    user=request.user,
                    image_name=image.name,
                    image_url=image_url,
                    thumbnail_url=thumbnail_url
                )

                uploaded_data.append({
                    "image_name": image.name,
                    "image_url": image_url,
                    "thumbnail_url": thumbnail_url
                })

            return Response({"uploaded": uploaded_data}, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Upload failed: {str(e)}")
            return Response({"detail": "Internal server error while uploading."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
