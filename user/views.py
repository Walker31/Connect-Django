from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from .models import Profile
from .serializer import ProfileSerializer
from .services import create_user_and_profile
from django.contrib.auth.models import User
from rest_framework.views import APIView


class SignupView(GenericAPIView):
    serializer_class = ProfileSerializer

    def post(self, request):
        data = request.data
        required = ["name", "password", "phone_no", "age", "latitude", "longitude"]
        missing = [f for f in required if not data.get(f)]

        if missing:
            return Response({"error": f"Missing fields: {', '.join(missing)}"}, status=400)

        if Profile.objects.filter(phone_no=data["phone_no"]).exists():
            return Response({"error": "Phone Number already registered."}, status=400)

        try:
            user, profile = create_user_and_profile(data)
            return Response({"message": f"User Created Successfully. Welcome, {user.first_name}!"}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class LoginView(GenericAPIView):
    serializer_class = ProfileSerializer

    def post(self, request):
        phone = request.data.get("phone_no")
        pwd = request.data.get("password")
        if not phone or not pwd:
            return Response({"error": "Phone number and password required."}, status=400)

        try:
            profile = Profile.objects.get(phone_no=phone)
            user = profile.user
            if authenticate(username=user.username, password=pwd):
                serialized = self.get_serializer(profile)
                return Response({
                    "message": f"Login Successful! Welcome, {user.first_name}.",
                    "token": "login",
                    "phone_no": phone,
                    "profile": serialized.data
                }, status=200)
            return Response({"error": "Wrong credentials."}, status=401)
        except Profile.DoesNotExist:
            return Response({"error": "Phone number not found."}, status=404)


class UpdateAccountView(GenericAPIView):
    serializer_class = ProfileSerializer

    def put(self, request):
        phone = request.data.get("phone_no")
        if not phone:
            return Response({"error": "Phone number required."}, status=400)

        try:
            profile = Profile.objects.get(phone_no=phone)
            for field in ["name", "age", "location"]:
                if field in request.data:
                    setattr(profile, field, request.data[field])
            profile.save()
            return Response({"message": "Account updated successfully."})
        except Profile.DoesNotExist:
            return Response({"error": "Profile not found."}, status=404)

class BulkSignupView(APIView):
    def post(self, request):
        users = request.data  # ✅ request.data is already a list
        created = []
        errors = []
        for u in users:
            if User.objects.filter(username=u["phone_no"]).exists():
                errors.append({
                    "user": u["phone_no"],
                    "error": "Phone number already registered."
                })
                continue
            try:
                
                user = User.objects.create_user(
                    username=u["phone_no"],
                    password=u["password"]
                )
                Profile.objects.create(
                    user=user,
                    name=u["username"],
                    gender=u["gender"],
                    phone_no=u["phone_no"],
                    age=u["age"],
                    latitude=u["latitude"],
                    longitude=u["longitude"],
                    interests=u.get("interests", [])
                )
                created.append(u["phone_no"])
            except Exception as e:
                errors.append({"user": u.get("phone_no"), "error": str(e)})

        return Response(
            {"created": created, "errors": errors},
            status=status.HTTP_201_CREATED if not errors else status.HTTP_207_MULTI_STATUS
        )
