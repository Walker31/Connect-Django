from django.http import JsonResponse
from rest_framework.response import Response 
from rest_framework import status
import math
from rest_framework.decorators import api_view, permission_classes # Import permissions
from rest_framework.permissions import IsAuthenticated             # Import IsAuthenticated
from user.models import Profile
import traceback
from django.db.models import Q # For complex lookups
import decimal # For high-precision math
import decimal

# The haversine function is good. No changes needed.
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (specified in decimal degrees).
    Returns the distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [float(lat1), float(lon1), float(lat2), float(lon2)])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    radius_of_earth_km = 6371  # Radius of Earth in kilometers
    return round(c * radius_of_earth_km, 2)

# -----------------------------------------------------------------
# OPTIMIZED `updateList`
# -----------------------------------------------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated]) # SECURITY: Only logged-in users can like
def updateList(request):
    try:
        # SECURITY FIX: Get the user from the request, not the request body.
        # This prevents a user from spoofing likes/dislikes for others.
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

        # Fetch the partner's profile
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

        match = False  # Default match state

        if action == "like":
            # OPTIMIZATION: Removed redundant 'isinstance(..., list)' check.
            # Your ArrayField(default=list) guarantees it's a list.
            
            # Check if the other user has *already* liked this user
            if user_profile.id in partner_profile.like:
                match = True
                # You might want to create a "Match" object here
            
            # Add to user's like list if not already present
            if other_id not in user_profile.like:
                user_profile.like.append(other_id)
                # Also remove from dislike list if it's there
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
                # Also remove from like list if it's there
                if other_id in user_profile.like:
                    user_profile.like.remove(other_id)
                user_profile.save(update_fields=["dislike", "like"])

            response_data = {
                "name": partner_profile.name,
                "status": "success",
                "match": False, # Cannot match on a dislike
                "message": "Disliked Profile successfully"
            }
            return Response(response_data, status=status.HTTP_200_OK)

    except Exception as e:
        traceback.print_exc() # For better logging
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

        # --- FIX IS HERE ---
        try:
            # 1. Get the radius as a Decimal, not a float
            radius_km = decimal.Decimal(request.query_params.get('radius', 10))
        except (ValueError, TypeError, decimal.InvalidOperation):
            return Response(
                {"error": "'radius' must be a valid number."}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        # --- END FIX ---

        current_lat = current_profile.latitude
        current_lon = current_profile.longitude

        # 2. Now all calculations are Decimal-based
        lat_change = radius_km / decimal.Decimal('111.045')
        
        # 3. Handle the 'cos' function, which needs a float but must return a Decimal
        cos_lat = decimal.Decimal(math.cos(math.radians(float(current_lat))))
        lon_change = radius_km / (decimal.Decimal('111.045') * cos_lat)
        
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
            print(f"Checking Profile ID: {profile.id}, Distance: {distance}, Radius: {radius_km}")
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