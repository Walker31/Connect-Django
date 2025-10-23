from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Profile
from django.contrib.auth.models import User

# --- Serializer for Reading Profile Data ---

class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for *displaying* Profile data.
    It automatically reads all defaults and validators from the Profile model.
    """

    class Meta:
        model = Profile
        fields = [
            'id', 
            'user',          # Represents the user's ID (PK)
            'name', 
            'gender', 
            'phone_no', 
            'location', 
            'latitude',      
            'longitude',     
            'about', 
            'age', 
            'profile_picture', 
            'pictures',
            'like',          
            'interests',     
            'dislike',       
            'last_online',   
            'created_at', 
            'updated_at',
        ]
        # These fields are set by the server, not the client
        read_only_fields = ['created_at', 'updated_at', 'last_online']


# --- Serializers for User Actions (Auth & Updates) ---

class SignupSerializer(serializers.Serializer):
    """
    Serializer for *validating* new user signups.
    """
    # Fields from User model
    password = serializers.CharField(write_only=True, style={'input_type': 'password'}, min_length=8)
    
    # Fields from Profile model
    name = serializers.CharField(max_length=255)
    phone_no = serializers.CharField(
        max_length=10,
        # Uses the regex from your model
        validators=[
            Profile._meta.get_field('phone_no').validators[0],
            # Also validates uniqueness
            UniqueValidator(
                queryset=Profile.objects.all(),
                message="A user with this phone number already exists."
            )
        ]
    )
    age = serializers.IntegerField(min_value=18, max_value=120)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    
    # Optional fields
    gender = serializers.CharField(max_length=15, required=False)
    interests = serializers.ListField(child=serializers.CharField(), required=False)

    def validate(self, data):
        # You can add more complex, multi-field validation here if needed
        return data


class LoginSerializer(serializers.Serializer):
    """
    Serializer for *validating* login credentials.
    """
    phone_no = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)


class UpdateProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for *updating* an existing profile.
    Only includes fields that are safe for a user to change.
    """
    class Meta:
        model = Profile
        fields = [
            'name',
            'gender',
            'location',
            'latitude',
            'longitude',
            'about',
            'age',
            'profile_picture',
            'pictures',
            'interests',
        ]
        # All fields are optional during an update (PATCH)
        extra_kwargs = {
            'name': {'required': False},
            'gender': {'required': False},
            'location': {'required': False},
            'latitude': {'required': False},
            'longitude': {'required': False},
            'about': {'required': False},
            'age': {'required': False},
            'profile_picture': {'required': False},
            'pictures': {'required': False},
            'interests': {'required': False},
        }