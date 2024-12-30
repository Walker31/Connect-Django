from django.http import JsonResponse
from django.core.serializers import serialize
import math
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from user.models import Profile

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
    return c * radius_of_earth_km

@csrf_exempt
@api_view(['GET'])
def find_profiles_within_radius(request, phone_no, radius_km=10):
    """
    Finds profiles within the specified radius of the provided profile's location coordinates.
    Args:
        request (HttpRequest): The request object.
        phone_no (str): The phone number of the profile to search around.
        radius_km (float): The radius in kilometers. Default is 10 km.

    Returns:
        JsonResponse: A JSON response with the nearby profiles or an error message.
    """
    try:
        # Get the current profile based on phone number
        current_profile = Profile.objects.get(phone_no=phone_no)
        current_coords = current_profile.locationCoordinates

        if not current_coords:
            return JsonResponse({"error": "Current profile does not have valid location coordinates."}, status=400)

        current_lat = current_coords.get('latitude')
        current_lon = current_coords.get('longitude')

        if current_lat is None or current_lon is None:
            return JsonResponse({"error": "Current profile's latitude or longitude is missing."}, status=400)

        nearby_profiles = []
        for profile in Profile.objects.exclude(id=current_profile.id):
            coords = profile.locationCoordinates
            if coords:
                lat = coords.get('latitude')
                lon = coords.get('longitude')

                if lat is not None and lon is not None:
                    distance = haversine(current_lat, current_lon, lat, lon)
                    if distance <= radius_km:
                        nearby_profiles.append({
                            "name": profile.name,
                            "phone_no": profile.phone_no,
                            "location": profile.location,
                            "locationCoordinates": profile.locationCoordinates,
                            "age": profile.age,
                        })

        return JsonResponse({"nearby_profiles": nearby_profiles}, status=200)

    except Profile.DoesNotExist:
        return JsonResponse({"error": "Profile with the given phone number does not exist."}, status=404)
    except Exception as e:
        return JsonResponse({"error": f"An error occurred: {str(e)}"}, status=500)
