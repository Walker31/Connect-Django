from .models import Profile
from django.contrib.auth.models import User
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from django.utils.crypto import get_random_string
from django.http import JsonResponse
from rest_framework.decorators import api_view
import json
from .serializer import ProfileSerializer

@csrf_exempt
@api_view(['POST'])
def signup(request):
    name = request.data.get('username')
    password = request.data.get('password')
    gender = request.data.get('gender')
    phone_no = request.data.get('phone_no')
    age = request.data.get('age')
    location = request.data.get('location')
    latitude = request.data.get('latitude')
    longitude = request.data.get('longitude')

    # Ensure all required fields are present
    if not all([name, password, phone_no, age, location, latitude, longitude]):
        return JsonResponse({"error": "All fields, including location coordinates, are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if phone number already exists
    if Profile.objects.filter(phone_no=phone_no).exists():
        return JsonResponse({"error": "Phone Number already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Generate a random username
        username = get_random_string(length=8)

        # Create user
        user = User.objects.create_user(username=username, password=password, first_name=name)

        # Create profile with location coordinates
        location_coordinates = {"latitude": float(latitude), "longitude": float(longitude)}
        profile = Profile(
            user=user, 
            phone_no=phone_no, 
            name=name, 
            age=age,
            gender = gender,
            location=location, 
            locationCoordinates=location_coordinates
        )
        profile.save()

        return JsonResponse({"message": f"User Created Successfully. Welcome, {name}!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@csrf_exempt
@api_view(['POST'])
def login_view(request):
    phone_no = request.data.get('phone_no')
    password = request.data.get('password')

    # Validate input fields
    if not phone_no or not password:
        return JsonResponse({"error": "Phone number and password are required."},status=status.HTTP_400_BAD_REQUEST)

    try:
        # Fetch the Profile and User
        profile = Profile.objects.get(phone_no=phone_no)
        user = profile.user

        # Authenticate the user
        authenticated_user = authenticate(username=user.username, password=password)

        if authenticated_user:
            serializer = ProfileSerializer(profile)
            return JsonResponse({"message": f"Login Successful! Welcome, {authenticated_user.first_name}.","profile":serializer.data},status=status.HTTP_200_OK)
        else:
            return JsonResponse({"error": "Wrong Credentials! Invalid phone number or password."},status=status.HTTP_401_UNAUTHORIZED)
    except Profile.DoesNotExist:
        return JsonResponse({"error": "Phone number does not exist."},status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['PUT'])
def update_account(request):
    try:
        phone_no = request.data.get('phone_no')

        if not phone_no:
            return JsonResponse({"error": "Phone number is required."},status=status.HTTP_400_BAD_REQUEST)

        # Fetch the profile by phone number
        try:
            profile = Profile.objects.get(phone_no=phone_no)
        except Profile.DoesNotExist:
            return JsonResponse({"error": "Phone number does not exist."},status=status.HTTP_404_NOT_FOUND)

        # Update only provided fields
        allowed_fields = ['name', 'age', 'location']
        for field, value in request.data.items():
            if field in allowed_fields:
                setattr(profile, field, value)

        # Save the updated profile
        profile.save()

        return JsonResponse({"message": "Account updated successfully."},status=status.HTTP_200_OK)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format."},status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
def bulk_signup(request):
    users_data = request.data.get('users')

    # Ensure the input is a list of users
    if not isinstance(users_data, list) or not users_data:
        return JsonResponse({"error": "A list of user data is required."}, status=status.HTTP_400_BAD_REQUEST)

    results = []

    for user_data in users_data:
        username = user_data.get('username')
        password = user_data.get('password')
        gender = user_data.get('gender')
        phone_no = user_data.get('phone_no')
        age = user_data.get('age')
        location = user_data.get('location')
        latitude = user_data.get('latitude')
        longitude = user_data.get('longitude')

        # Validate required fields
        if not all([username, password, phone_no, age, location, latitude, longitude]):
            results.append({
                "phone_no": phone_no,
                "status": "failed",
                "error": "All fields, including location coordinates, are required."
            })
            continue

        # Check if phone number already exists
        if Profile.objects.filter(phone_no=phone_no).exists():
            results.append({
                "phone_no": phone_no,
                "status": "failed",
                "error": "Phone Number already registered."
            })
            continue

        try:
            # Create user
            user = User.objects.create_user(username=username, password=password, first_name=username)

            # Create profile with location coordinates
            location_coordinates = {"latitude": float(latitude), "longitude": float(longitude)}
            profile = Profile(
                user=user,
                phone_no=phone_no,
                name=username,
                age=age,
                gender=gender,
                location=location,
                locationCoordinates=location_coordinates
            )
            profile.save()

            results.append({
                "phone_no": phone_no,
                "status": "success",
                "message": f"User Created Successfully. Welcome, {username}!"
            })
        except Exception as e:
            results.append({
                "phone_no": phone_no,
                "status": "failed",
                "error": f"An error occurred: {str(e)}"
            })

    return JsonResponse({"results": results}, status=status.HTTP_207_MULTI_STATUS)
