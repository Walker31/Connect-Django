from django.urls import path
from . import views

urlpatterns = [
    path("", views.list_posts, name="list_posts"),
    path("create/", views.create_post, name="create_post"),
    path("<int:post_id>/", views.detail_post, name="detail_post"),
    path("update/", views.update_post, name="update_post"),
    path("delete/", views.delete_post, name="delete_post"),
]
