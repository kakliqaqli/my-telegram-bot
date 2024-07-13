import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from starlette.routing import Mount, Router
from starlette.staticfiles import StaticFiles

from . import settings
from .routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
django_asgi_app = get_asgi_application()

# Starlette application
starlette_router = Router([
    Mount('/static', StaticFiles(directory=settings.BASE_DIR / 'static'), name='static'),
    Mount('/media', StaticFiles(directory=settings.BASE_DIR / 'media'), name='media'),
    Mount('/sounds', StaticFiles(directory=settings.BASE_DIR / 'sounds'), name='sounds'),
    Mount('/', django_asgi_app),
])

app = ProtocolTypeRouter({
    "http": starlette_router,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
    ),
})
