from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .account_functions import create_account, login_account, update_account

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        phone_no = data.get('phone_no')
        about = data.get('about')
        profile_picture = data.get('profile_picture')

        response = create_account(
            username=username,
            password=password,
            phone_no=phone_no,
            about=about,
            profile_picture=profile_picture
        )
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        phone_no = data.get('phone_no')
        password = data.get('password')

        response = login_account(phone_no=phone_no, password=password)
        return JsonResponse(response,status = 200)

    return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
def update_account(request, user_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        response = update_account(user_id=user_id, **data)
        return JsonResponse(response)

    return JsonResponse({"error": "Invalid request method"}, status=400)
