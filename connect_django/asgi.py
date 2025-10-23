# connect_django/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack # Comment out or remove if only using token auth
from .middleware import TokenAuthMiddleware # Import your middleware
import messaging.routing # Make sure this points to your chat app's routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'connect_django.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddleware( # Wrap the URLRouter
        URLRouter(
            messaging.routing.websocket_urlpatterns
        )
    ),
})