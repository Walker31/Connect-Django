from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import FileUploadForm
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from azure.storage.blob import BlobServiceClient
from django.conf import settings
import logging

# Initialize logging
logger = logging.getLogger(__name__)

@login_required
def index(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.save(commit=False)
            upload.profile = request.user
            upload.save()
            return redirect('/')
        else:
            context = {'form': form}
            return render(request, 'index.html', context)
    context = {'form': FileUploadForm()}
    return render(request, 'index.html', context)

@api_view(['POST'])
def upload_image(request):
    if request.method == 'POST':
        images = request.FILES.getlist('images')
        uploaded_image_urls = []

        if not images:
            return Response({"detail": "No images provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Initialize the BlobServiceClient using the connection string
            blob_service_client = BlobServiceClient.from_connection_string(settings.AZURE_CONNECTION_STRING)
            container_client = blob_service_client.get_container_client(settings.AZURE_CONTAINER)

            for image in images:
                # Create a BlobClient to interact with the blob
                blob_client = container_client.get_blob_client(image.name)

                # Check if the file already exists
                if blob_client.exists():
                    logger.warning(f"File {image.name} already exists. Overwriting it.")
                    overwrite = True
                else:
                    overwrite = True  # Or you can check if the user wants to upload a new version

                # Upload the image to Azure Blob Storage
                blob_client.upload_blob(image, overwrite=overwrite)
                
                # Append the URL of the uploaded image to the list
                uploaded_image_urls.append(blob_client.url)

            return Response({
                'image_urls': uploaded_image_urls
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error uploading images: {str(e)}")
            return Response({"detail": "Error uploading images. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

