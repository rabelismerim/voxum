import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from config.token_auth import TokenAuthMiddlewareStack
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.core.asgi import get_asgi_application
from apps.web_sockets.urls_sockets import websockets
from config.settings import ENABLE_TOKEN
from apps.web_sockets.signals import signal_started_sockets

django_asgi_app = get_asgi_application()

protocol_routers = {
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            websockets
        )
    )
}

if ENABLE_TOKEN:
    # Enable Token authentication
    protocol_routers['websocket'] = AuthMiddlewareStack(TokenAuthMiddlewareStack(websockets))

application = ProtocolTypeRouter(protocol_routers)

signal_started_sockets.send('application')