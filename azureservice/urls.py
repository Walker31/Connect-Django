from django.urls import path
from .views import IndexView, UploadImageView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('upload', UploadImageView.as_view(), name='upload_image'),
]
