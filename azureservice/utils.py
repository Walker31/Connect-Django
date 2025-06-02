from PIL import Image
from io import BytesIO

def generate_thumbnail(image_file, size=(300, 300)):
    """
    Generate a thumbnail from an uploaded image and return it as a BytesIO stream.

    :param image_file: InMemoryUploadedFile from request.FILES
    :param size: Desired thumbnail size (width, height)
    :return: BytesIO object containing thumbnail image
    """
    try:
        image = Image.open(image_file)
        image.convert("RGB")  # Ensure JPEG-compatible
        image.thumbnail(size, Image.ANTIALIAS)

        thumb_io = BytesIO()
        image.save(thumb_io, format='JPEG', quality=85)
        thumb_io.seek(0)  # Important for reading in Azure upload

        return thumb_io
    except Exception as e:
        raise RuntimeError(f"Failed to generate thumbnail: {str(e)}")
