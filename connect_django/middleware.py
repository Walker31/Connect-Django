# connect_django/middleware.py
import jwt
from django.conf import settings
from django.contrib.auth.models import AnonymousUser, User
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from urllib.parse import parse_qs
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

@database_sync_to_async
def get_user(user_id):
    try:
        # Make sure you're fetching the User model, not Profile
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware(BaseMiddleware):
    """
    Custom middleware that takes a token from the query string
    and authenticates the user for WebSockets.
    """
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]

        if token:
            try:
                access_token = AccessToken(token)
                user_id = access_token.payload.get('user_id')
                if user_id:
                    scope['user'] = await get_user(user_id)
                else:
                    scope['user'] = AnonymousUser()
            except (InvalidToken, TokenError) as e:
                print(f"WebSocket Auth Error: Invalid/Expired Token - {e}")
                scope['user'] = AnonymousUser()
        else:
            scope['user'] = AnonymousUser()

        # print(f"WebSocket User: {scope['user']}") # Optional: for debugging

        return await super().__call__(scope, receive, send)