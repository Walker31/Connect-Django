from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255, blank=True, null=True)
    gender = models.CharField(max_length=10, blank=True, null=True)
    like = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True,
    )
    interests = ArrayField(
        models.CharField(max_length=255),
        default=list,
        blank=True,
        help_text="A list of user's interests stored as an array of strings."
    )
    dislike = ArrayField(
        models.IntegerField(),
        default=list,
        blank=True,
    )
    phone_no = models.CharField(
        max_length=10,
        unique=True,
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')],
        blank=True,
        null=True
    )
    location = models.CharField(max_length=255, blank=True, null=True)
    locationCoordinates = models.JSONField(
        blank=True,
        null=True,
        help_text="Store location coordinates as {'latitude': value, 'longitude': value}."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    about = models.TextField(max_length=1024, blank=True, null=True)
    age = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Age of the user."
    )
    last_online = models.DateTimeField(
        blank=True,
        null = True,
        help_text="Stores the timestamp of the user's last online activity."
    )
    profile_picture = models.URLField(
        max_length=2048,
        blank=True,
        null=True,
        default="https://example.com/default-profile-picture.png",
        help_text="URL to the user's profile picture."
    )
    pictures = models.JSONField(
        blank=True,
        null=True,
        help_text="Store additional profile pictures as a JSON object, e.g., {'images': [url1, url2]}."
    )

    def save(self, *args, **kwargs):
        if not self.name and self.user:
            self.name = self.user.username
        if self.phone_no and not self.phone_no.isdigit():
            raise ValueError("Phone number must contain only digits.")
        super().save(*args, **kwargs)
    
    def set_location_coordinates(self, latitude, longitude):
        self.locationCoordinates = {"latitude": latitude, "longitude": longitude}
        self.save()

    def update_last_online(self):
        """Update the last_online field with the current timestamp."""
        self.last_online = now()
        self.save(update_fields=["last_online"])
    
    def __str__(self):
        return self.name if self.name else self.user.username
    
    class Meta:
        db_table = 'profiles'
        managed = True
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"
        indexes = [
            models.Index(fields=['phone_no']),
            models.Index(fields=['locationCoordinates']),
        ]
