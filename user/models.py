from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.timezone import now
from django.contrib.postgres.fields import ArrayField

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"  # Allows reverse lookup: `user.profile`.
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    phone_no = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')],
        blank=True,
        null=True
    )
    location = models.CharField(max_length=255,blank = True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    about = models.TextField(max_length=512, blank=True, null=True)

    # New fields
    profile_picture = models.URLField(
        max_length=2048,
        blank=True,
        null=True,
        help_text="URL to the user's profile picture."
    )
    pictures = ArrayField(models.CharField(max_length=255), blank=True, null=True)  # Array for storing multiple image URLs or paths


    def save(self, *args, **kwargs):
        # Automatically set the name to username if not provided.
        if not self.name and self.user:
            self.name = self.user.username
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name if self.name else self.user.username

    class Meta:
        db_table = 'profiles'
        managed = True
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
