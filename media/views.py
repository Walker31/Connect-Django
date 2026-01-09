import cloudinary
import cloudinary.uploader
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.conf import settings
from .models import ImageUpload
import logging

logger = logging.getLogger(__name__)


class UploadImageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        images = request.FILES.getlist('images')
        uploaded_data = []

        if not images:
            return Response(
                {"detail": "No images provided."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if len(images) > 6:
            return Response(
                {"detail": "You can upload a maximum of 6 images at a time."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Configure Cloudinary
            cloudinary.config(
                cloud_name=settings.CLOUDINARY_CLOUD_NAME,
                api_key=settings.CLOUDINARY_API_KEY,
                api_secret=settings.CLOUDINARY_API_SECRET
            )

            for image in images:
                try:
                    # Upload to Cloudinary with transformations
                    upload_result = cloudinary.uploader.upload(
                        image,
                        folder='Connect/profiles',
                        resource_type='auto',
                        transformation=[
                            {'width': 500, 'height': 500, 'crop': 'fill'}
                        ]
                    )

                    image_url = upload_result.get('secure_url')
                    public_id = upload_result.get('public_id')

                    # Generate thumbnail URL
                    thumbnail_url = cloudinary.CloudinaryResource(public_id).build_url(
                        width=300,
                        height=300,
                        crop='fill'
                    )

                    # Save to database
                    image_upload = ImageUpload.objects.create(
                        user=request.user,
                        image_name=image.name,
                        image_url=image_url,
                        thumbnail_url=thumbnail_url,
                        public_id=public_id
                    )

                    uploaded_data.append({
                        "id": image_upload.id,
                        "image_name": image.name,
                        "image_url": image_url,
                        "thumbnail_url": thumbnail_url
                    })

                except Exception as e:
                    logger.error(f"Failed to upload {image.name}: {str(e)}")
                    return Response(
                        {"detail": f"Failed to upload {image.name}: {str(e)}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(
                {"uploaded": uploaded_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Upload error: {str(e)}")
            return Response(
                {"detail": f"Internal server error: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
