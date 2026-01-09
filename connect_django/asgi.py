# connect_django/asgi.py
import os
import django

# Set Django settings BEFORE any imports
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "connect_django.settings")
django.setup()

from django.core.asgi import get_asgi_application  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from .middleware import TokenAuthMiddleware  # noqa: E402
import messaging.routing  # noqa: E402

django.setup()


application = ProtocolTypeRouter(
    {
        "http": get_asgi_application(),
        "websocket": TokenAuthMiddleware(
            URLRouter(messaging.routing.websocket_urlpatterns)
        ),
    }
)
