from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class WebSocketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.web_sockets'

    def ready(self):

        # Auto Discover modules to sockets
        for app in settings.INSTALLED_APPS:
            try:
                import_module(f'{app}.sockets')
            except (AttributeError, ModuleNotFoundError):
                continue
