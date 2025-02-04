from django.http import JsonResponse
from django.core.serializers import serialize
import math
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from user.models import Profile
from django.shortcuts import get_object_or_404

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two points on the Earth (specified in decimal degrees).
    Returns the distance in kilometers.
    """
    # Convert latitude and longitude from degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.asin(math.sqrt(a))
    radius_of_earth_km = 6371  # Radius of Earth in kilometers
    return round(c * radius_of_earth_km,2)


@api_view(['POST'])
def updateList(request):
    try:
        id = request.data.get('id')  # ID of the user performing the action
        other_id = request.data.get('other_id')  # Partner's ID
        action = request.data.get('action')  

        if not id or not other_id or not action:
            return JsonResponse({"status": "error", "message": "Missing required parameters"}, status=400)
        # Fetch both user profiles
        user_profile = Profile.objects.filter(id=id).first()
        partner_profile = Profile.objects.filter(id=other_id).first()
        if not user_profile or not partner_profile:
            return JsonResponse({"status": "error", "message": "Invalid user or partner ID"}, status=404)

        match = False  # Default match state

        if action == "like":
            # Check if the current user's ID is already in the partner's like array
            if id in partner_profile.like:
                # It's a match!
                match = True
            else:
                # Add the partner's ID to the user's like array
                if other_id not in user_profile.like:
                    user_profile.like.append(other_id)
                    user_profile.save()

            return JsonResponse({
                "status": "success",
                "match": match,
                "message": "Liked Profile successfully"
            })

        elif action == "dislike":
            # Add the partner's ID to the user's dislike array
            if other_id not in user_profile.dislike:
                user_profile.dislike.append(other_id)
                user_profile.save()
            return JsonResponse({
                "status": "success",
                "match": match,
                "message": "Disliked Profile successfully"
            })

        else:
            return JsonResponse({"status": "error", "message": "Invalid action"}, status=400)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)



@csrf_exempt
@api_view(['GET'])
def find_profiles(request, radius_km=5):
    """
    Finds profiles within the specified radius of the provided profile's location coordinates.

    Args:
        request (HttpRequest): The request object.
        radius_km (float): The radius in kilometers. Default is 10 km.

    Returns:
        JsonResponse: A JSON response with the nearby profiles or an error message.
    """
    try:
        # Get phone_no from query parameters
        phone_no = request.GET.get('phone_no')
        if not phone_no:
            return JsonResponse({"error": "Phone number is required as a query parameter."}, status=400)

        # Fetch the profile based on phone number
        current_profile = Profile.objects.get(phone_no=phone_no)
        current_coords = current_profile.locationCoordinates

        # Validate location coordinates
        if not current_coords or 'latitude' not in current_coords or 'longitude' not in current_coords:
            return JsonResponse(
                {"error": "Current profile does not have valid latitude and longitude coordinates."}, 
                status=400
            )

        current_lat = float(current_coords['latitude'])
        current_lon = float(current_coords['longitude'])
        count = 0
        user = current_profile.user
        nearby_profiles = []
        # Iterate through all profiles except the current one
        for profile in Profile.objects.exclude(id=current_profile.id):
            if current_profile.gender == profile.gender:
                continue
            coords = profile.locationCoordinates
            if coords and 'latitude' in coords and 'longitude' in coords:
                lat = float(coords['latitude'])
                lon = float(coords['longitude'])
                distance = haversine(current_lat, current_lon, lat, lon)
                if distance <= radius_km:
                    count +=1   
                    nearby_profiles.append({
                        "id": profile.id,
                        "name": profile.name,
                        "gender": profile.gender,
                        "phone_no": profile.phone_no,
                        "location": profile.location,
                        "locationCoordinates": profile.locationCoordinates,
                        "age": profile.age, 
                        "distance":distance,
                    })

        return JsonResponse({"nearby_profiles": nearby_profiles,"total_profile" : count}, status=200)

    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile with the given phone number does not exist."}, status=404)
    except KeyError as e:
        return JsonResponse({"error": f"Missing data in profile coordinates: {str(e)}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

