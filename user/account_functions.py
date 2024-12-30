from django.contrib.auth.models import User
from .models import Profile
from django.db import transaction
from django.core.exceptions import ValidationError

def create_account(username, password, phone_no=None, about=None, profile_picture=None):
    try:
        with transaction.atomic():
            # Create User
            user = User.objects.create_user(username=username, password=password)

            # Create Profile
            profile = Profile.objects.create(
                user=user,
                phone_no=phone_no,
                about=about,
                profile_picture=profile_picture
            )

        return {"success": True, "user_id": user.id, "profile_id": profile.id}

    except Exception as e:
        return {"success": False, "error": str(e)}

def update_account(user_id, **kwargs):
    """
    Update user and profile details.
    Args:
        user_id: ID of the User to update.
        kwargs: Fields to update in User or Profile.

    Returns:
        Success message or error.
    """
    try:
        user = User.objects.get(id=user_id)
        profile = Profile.objects.get(user=user)

        # Update User fields
        if "username" in kwargs:
            user.username = kwargs["username"]

        user.save()

        # Update Profile fields
        if "phone_no" in kwargs:
            profile.phone_no = kwargs["phone_no"]
        if "about" in kwargs:
            profile.about = kwargs["about"]
        if "profile_picture" in kwargs:
            profile.profile_picture = kwargs["profile_picture"]
        if "pictures" in kwargs:
            profile.pictures = kwargs["pictures"]

        profile.save()

        return {"success": True, "message": "Account updated successfully"}

    except User.DoesNotExist:
        return {"success": False, "error": "User not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

from django.contrib.auth import authenticate

from django.contrib.auth import authenticate
from .models import Profile

def login_account(phone_no, password):
    """
    Authenticate the user using phone number and password.
    Args:
        phone_no: Phone number of the user.
        password: Password of the user.

    Returns:
        Success message with user details or error.
    """
    try:
        # Find the associated User object using the phone number.
        profile = Profile.objects.get(phone_no=phone_no)
        user = profile.user

        # Authenticate the user
        user = authenticate(username=user.username, password=password)

        if user:
            return {
                "success": True,
                "user_id": user.id,
                "username": user.username,
            }
        else:
            return {"success": False, "error": "Invalid phone number or password"}

    except Profile.DoesNotExist:
        return {"success": False, "error": "Phone number not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}
