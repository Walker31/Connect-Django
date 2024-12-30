from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    post_text = models.CharField(max_length=512)
    author = models.ForeignKey(
        User,  # Reference to the `User` model.
        on_delete=models.CASCADE,
        related_name='posts'  # Allows reverse lookup, e.g., `user.posts`.
    )
    interest = models.CharField(max_length=512)
    pic = models.URLField(max_length=2048, blank=True, null=True)  # Assuming pic is a URL.
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when created.
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updated on save.

    def __str__(self):
        return f"{self.author.username}: {self.post_text[:50]}"  # Display a snippet of the post text.

    class Meta:
        db_table = 'posts'
        managed = True
