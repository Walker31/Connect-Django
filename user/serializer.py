from rest_framework import serializers
from .models import Profile
from django.contrib.auth.models import User

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    locationCoordinates = serializers.JSONField(required=False, default=dict)  # Default to empty dict if null
    profile_picture = serializers.URLField(required=False, default="https://example.com/default-profile-picture.png")  # Default URL if null
    pictures = serializers.JSONField(required=False, default=list)  # Default to empty list if null
    name = serializers.CharField(required=False, default=None)  # Default to None if null
    gender = serializers.CharField(required=False, default="Not Specified")  # Default to "Not Specified"
    phone_no = serializers.CharField(required=False, default=None)  # Default to None if null
    location = serializers.CharField(required=False, default="Unknown")  # Default to "Unknown" if null
    about = serializers.CharField(required=False, default="No description provided.")  # Default text if null
    age = serializers.IntegerField(required=False, default=None)  # Default to None if null

    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'name', 'gender', 'phone_no', 'location', 'locationCoordinates', 
            'created_at', 'updated_at', 'about', 'age', 'profile_picture', 'pictures'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_phone_no(self, value):
        if value and not value.isdigit():
            raise serializers.ValidationError("Phone number must contain only digits.")
        return value
