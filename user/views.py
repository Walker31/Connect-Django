# Imports from Django and DRF
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Q
import math
import decimal
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import traceback

from connect_django import settings

# Local imports
from .models import Profile
from .services import create_user_and_profile
from .serializers import (
    LoginSerializer,
    ProfileSerializer,
    SignupSerializer,
    UpdateProfileSerializer
)

# --- Auth and Account Views ---

class SignupView(GenericAPIView):
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user, profile = create_user_and_profile(serializer.validated_data)
            return Response(
                {"message": f"User Created Successfully. Welcome, {user.first_name}!"},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response({"error": "An internal error occurred during user creation."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data.get("phone_no")
        pwd = serializer.validated_data.get("password")

        try:
            profile = Profile.objects.select_related('user').get(phone_no=phone)
            user = profile.user

            if authenticate(username=user.username, password=pwd):
                output_serializer = ProfileSerializer(profile)
                refresh = RefreshToken.for_user(user)

                return Response({
                    "message": f"Login Successful! Welcome, {profile.name}.",
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "profile": output_serializer.data
                }, status=status.HTTP_200_OK)

            return Response({"error": "Wrong credentials."}, status=status.HTTP_401_UNAUTHORIZED)
        except Profile.DoesNotExist:
            return Response({"error": "Phone number not found."}, status=status.HTTP_404_NOT_FOUND)


class AccountView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateProfileSerializer

    def get_object(self):
        return self.request.user.profile

    def get(self, request):
        profile = self.get_object()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            "message": "Account updated successfully.",
            "profile": serializer.data
        }, status=status.HTTP_200_OK)


class BulkSignupView(APIView):
    def post(self, request):
        users_data = request.data
        if not isinstance(users_data, list):
            return Response(
                {"error": "Expected a list of user objects."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_phones = []
        errors = []

        incoming_phones = [
            u.get("phone_no") for u in users_data if u.get("phone_no")
        ]

        existing_phones = set(
            User.objects.filter(username__in=incoming_phones).values_list('username', flat=True)
        )

        for u_data in users_data:
            phone = u_data.get("phone_no")

            if not phone:
                errors.append({"user_data": u_data, "error": "Missing 'phone_no'."})
                continue

            if phone in existing_phones:
                errors.append({"user": phone, "error": "Phone number already registered."})
                continue

            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=phone,
                        password=u_data.get("password"),
                        first_name=u_data.get("username", "")
                    )
                    Profile.objects.create(
                        user=user,
                        name=u_data.get("username", ""),
                        gender=u_data.get("gender"),
                        phone_no=phone,
                        age=u_data.get("age"),
                        latitude=u_data.get("latitude"),
                        longitude=u_data.get("longitude"),
                        interests=u_data.get("interests", [])
                    )
                    created_phones.append(phone)
                    existing_phones.add(phone)

            except Exception as e:
                errors.append({"user": phone, "error": str(e)})

        status_code = status.HTTP_207_MULTI_STATUS if errors else status.HTTP_201_CREATED

        return Response(
            {"created": created_phones, "errors": errors},
            status=status_code
        )

# --- App-Specific Views (Matching, Finding) ---

def haversine(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    radius_of_earth_km = 6371
    return round(c * radius_of_earth_km, 2)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def updateList(request):
    try:
        user_profile = request.user.profile
        
        try:
            other_id = int(request.data.get('other_id'))
        except (ValueError, TypeError):
            return Response(
                {"status": "error", "message": "'other_id' must be a valid integer"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        action = request.data.get('action')
        if not action or action not in ["like", "dislike"]:
            return Response(
                {"status": "error", "message": "Missing or invalid 'action' (must be 'like' or 'dislike')"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            partner_profile = Profile.objects.get(id=other_id)
        except Profile.DoesNotExist:
            return Response(
                {"status": "error", "message": "Partner profile not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if user_profile.id == partner_profile.id:
            return Response(
                {"status": "error", "message": "Cannot like or dislike yourself"},
                status=status.HTTP_400_BAD_REQUEST
            )

        match = False

        if action == "like":
            if user_profile.id in partner_profile.like:
                match = True
            
            if other_id not in user_profile.like:
                user_profile.like.append(other_id)
                if other_id in user_profile.dislike:
                    user_profile.dislike.remove(other_id)
                user_profile.save(update_fields=["like", "dislike"])

            response_data = {
                "name": partner_profile.name,
                "status": "success",
                "match": match,
                "message": "Liked Profile successfully"
            }
            return Response(response_data, status=status.HTTP_200_OK)

        elif action == "dislike":
            if other_id not in user_profile.dislike:
                user_profile.dislike.append(other_id)
                if other_id in user_profile.like:
                    user_profile.like.remove(other_id)
                user_profile.save(update_fields=["dislike", "like"])

            response_data = {
                "name": partner_profile.name,
                "status": "success",
                "match": False,
                "message": "Disliked Profile successfully"
            }
            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        traceback.print_exc()
        return Response(
            {"status": "error", "message": "An internal server error occurred"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def find_profiles(request):
    try:
        current_profile = request.user.profile
        
        if current_profile.latitude is None or current_profile.longitude is None:
            return Response(
                {"error": "Your profile is missing location data. Please update your location."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            radius_km = float(request.query_params.get('radius', 5))
        except (ValueError, TypeError):
            return Response(
                {"error": "'radius' must be a valid number."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        current_lat = current_profile.latitude
        current_lon = current_profile.longitude

        lat_change = radius_km / decimal.Decimal('111.045')
        lon_change = radius_km / (decimal.Decimal('111.045') * decimal.Decimal(math.cos(math.radians(current_lat))))
        
        lat_min = current_lat - lat_change
        lat_max = current_lat + lat_change
        lon_min = current_lon - lon_change
        lon_max = current_lon + lon_change
        
        seen_ids = set(current_profile.like) | set(current_profile.dislike)
        seen_ids.add(current_profile.id)

        potential_matches = Profile.objects.filter(
            latitude__range=(lat_min, lat_max),
            longitude__range=(lon_min, lon_max),
            latitude__isnull=False,
            longitude__isnull=False
        ).exclude(
            id__in=seen_ids
        ).exclude(
            gender=current_profile.gender
        )
        
        nearby_profiles = []
        for profile in potential_matches:
            distance = haversine(current_lat, current_lon, profile.latitude, profile.longitude)
            
            if distance <= radius_km:
                nearby_profiles.append({
                    "id": profile.id,
                    "name": profile.name,
                    "gender": profile.gender,
                    "age": profile.age, 
                    "distance": distance,
                    "profile_picture": profile.profile_picture,
                    "about": profile.about,
                })
        
        nearby_profiles.sort(key=lambda p: p["distance"])
        
        return Response(
            {"total_profiles": len(nearby_profiles), "nearby_profiles": nearby_profiles},
            status=status.HTTP_200_OK
        )

    except Profile.DoesNotExist:
        return Response(
            {"error": "Profile not found. This should not happen if authenticated."}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        traceback.print_exc()
        return Response(
            {"error": f"An unexpected error occurred: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

class GoogleLoginView(APIView):
    def post(self,request):
        token = request.data.get('token')
        if not token:
            return Response({"error":"No Token provided in request body"},status = status.HTTP_400_BAD_REQUEST)
        try:
            id_info = id_token.verify_oauth2_token(token,google_requests.Request(),settings.GOOGLE_CLIENT_ID)
            email = id_info['email']
            name = id_info['name']
            google_id = id_info.get('sub')
            if not email:
                return Response({"error":"Email not found in Google token"},status = status.HTTP_400_BAD_REQUEST)
            
            try:
                user = User.objects.get(email=email)
                profile = user.profile
                refresh = RefreshToken().for_user(user=user)
                return Response({'message':f"Login Successful! Welcome, {profile.name}.",'refresh':str(refresh),'access':str(refresh.access_token),'profile':ProfileSerializer(profile).data,'new_user':False},status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'new_user':True,'email':email,'name':name,'profile_picture':id_info.get('picture')},status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": f"Invalid token: {str(e)}"}, status=status.HTTP_401_UNAUTHORIZED)
        except Profile.DoesNotExist:
             return Response({"error": "Profile missing"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            traceback.print_exc()
            return Response({"error": f"An error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)