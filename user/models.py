from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.contrib.postgres.fields import ArrayField
from django.utils.timezone import now

class Profile(models.Model):
    # No 'id' field needed, Django adds 'id = AutoField(primary_key=True)' by default
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=255, blank=True, null=True)
    
    # Moved default from serializer to model
    gender = models.CharField(max_length=15, blank=True, null=True, default="Not Specified")
    
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
        # This validator is automatically used by ModelSerializer
        validators=[RegexValidator(r'^\d{10}$', 'Enter a valid 10-digit phone number')],
        blank=True,
        null=True
    )
    
    # Moved default from serializer to model
    location = models.CharField(max_length=255, blank=True, null=True, default="Unknown")
    
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Moved default from serializer to model
    about = models.TextField(max_length=1024, blank=True, null=True, default="No description provided.")
    
    age = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(120)],
        help_text="Age of the user."
    )
    last_online = models.DateTimeField(
        blank=True,
        null=True,
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
        default=list,  # Changed from null=True to default=list
        blank=True,
        help_text="Store additional profile pictures as a JSON list, e.g., [url1, url2]."
    )

    def save(self, *args, **kwargs):
        if not self.name and self.user:
            self.name = self.user.username
        
        # REMOVED: This check is redundant.
        # The RegexValidator on the field is stronger and handles this.
        # if self.phone_no and not self.phone_no.isdigit():
        #     raise ValueError("Phone number must contain only digits.")
        
        super().save(*args, **kwargs)

    def set_location_coordinates(self, latitude, longitude):
        """Set location coordinates (latitude, longitude) and save."""
        self.latitude = latitude
        self.longitude = longitude
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
        ]