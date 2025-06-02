from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
from .models import Profile

def create_user_and_profile(data):
    username = get_random_string(length=8)
    user = User.objects.create_user(username=username, password=data["password"], first_name=data["name"])
    profile = Profile.objects.create(
        user=user,
        name=data["name"],
        phone_no=data["phone_no"],
        gender=data.get("gender", "Not Specified"),
        interests=data.get("interests", []),
        age=data["age"],
        location="TDA",
        latitude=data["latitude"],
        longitude=data["longitude"]
    )
    return user, profile
