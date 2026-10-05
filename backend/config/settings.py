import logging
import sysconfig
import os
import base64
import hashlib
from os import path

from celery.exceptions import CPendingDeprecationWarning
from decouple import config
from kombu import Exchange, Queue

import warnings
from cryptography.fernet import Fernet

warnings.filterwarnings("ignore", category=CPendingDeprecationWarning)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

SOCKET_PORT = config('SOCKET_PORT', cast=str, default='8001')

from config.settings_base import *

INSTALLED_APPS += [
    'django_celery_results',
    'django_redis',
    'core',
    'core.permissions',
    'apps.voxum_base',
    'apps.creditor',
    'apps.guest',
    'apps.meetings',
    'apps.recovering',
    'apps.voting',
    'apps.voting.big_number',
    'apps.web_sockets',
    'apps.location',
    'apps.presence',
    'apps.works',
    'apps.report',

    'support.schedule',

    'django_apscheduler',
]


def add_security_headers(headers, path_url, url):
    headers.add_header('X-Content-Type-Options', 'nosniff')
    headers.add_header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains; preload')
    headers.add_header('X-XSS-Protection', '1; mode=block')
    headers.add_header(
        'Content-Security-Policy',
        "default-src 'self'; frame-ancestors 'none'; object-src 'none'; base-uri 'self'",
    )
    headers.add_header('Referrer-Policy', 'no-referrer-when-downgrade')
    headers.add_header('Cross-Origin-Opener-Policy', 'same-origin')
    headers.add_header('Vary', 'Cookie, Accept-Language')
    headers.add_header('X-Frame-Options', 'DENY')
    return headers


if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(2, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATICFILES_STORAGE = "config.storage.CustomManifestStaticFilesStorage"
WHITENOISE_ALLOW_ALL_ORIGINS = False
WHITENOISE_ADD_HEADERS_FUNCTION = add_security_headers


def ratelimit_view(request, *args, **kwargs):
    if request.path == '/url1/' or request.path == '/url2/':
        return True
    return False


SECRET_KEY_GUEST = config('SECRET_KEY_GUEST', cast=str, default=SECRET_KEY if ENV_DEV else '')
SECRET_KEY_INTRANET = config('SECRET_KEY_INTRANET', cast=str, default=SECRET_KEY if ENV_DEV else '')
FERNET_KEY_VALUE = config(
    'FERNET_KEY',
    cast=str,
    default=base64.urlsafe_b64encode(hashlib.sha256(f'{SECRET_KEY}:voxum-fernet'.encode()).digest()).decode()
    if ENV_DEV else '',
)
if not FERNET_KEY_VALUE:
    raise RuntimeError('FERNET_KEY must be configured outside local development.')
FERNET_KEY = FERNET_KEY_VALUE.encode()
ENABLE_TOKEN = config('ENABLE_TOKEN', cast=bool, default=True)
ENABLE_PW = config('ENABLE_PW', cast=bool, default=False)
TOKEN_TEST = config('TOKEN_TEST', cast=bool, default=False)

RATELIMIT_VIEW = ratelimit_view

HOST_TESTS = config('HOST_TESTS', default='')
HOST_VERIFY = config('HOST_VERIFY', default=not ENV_DEV, cast=bool)
channel_redis_url = config('REDIS_URL', default='redis://localhost:6379/6')
channel_redis_cache = config('REDIS_URL', default='redis://localhost:6379/7')
celery_url = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/8')

if ENV_DEV:
    CHANNEL_LAYERS = {
        name: {'BACKEND': 'channels.layers.InMemoryChannelLayer'}
        for name in ('default', 'guest', 'intranet', 'general_intranet')
    }
else:
    CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'apps.web_sockets.channel_layer.ExtendedRedisChannelLayer',
        'CONFIG': {
            "hosts": [channel_redis_url],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 500,
        },
    },
    'guest': {
        'BACKEND': 'apps.web_sockets.channel_layer.ExtendedRedisChannelLayer',
        'CONFIG': {
            "hosts": [channel_redis_url],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 500,
        },
    },
    'intranet': {
        'BACKEND': 'apps.web_sockets.channel_layer.ExtendedRedisChannelLayer',
        'CONFIG': {
            "hosts": [channel_redis_url],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 500,
        },
    },
    'general_intranet': {
        'BACKEND': 'apps.web_sockets.channel_layer.ExtendedRedisChannelLayer',
        'CONFIG': {
            "hosts": [channel_redis_url],
            "symmetric_encryption_keys": [SECRET_KEY],
            "capacity": 500,
        },
    },
    }

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES[0]['DIRS'].append(os.path.join(DIR, 'templates'))
BASE_SOCKETS = f'{APP_NAME}/ws/V1/'
BASE_SOCKETS_GUEST = f'{APP_NAME}/ws/V1/guest/'

REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
    'rest_framework.permissions.IsAuthenticated',
    'core.permissions.views.IsUserManagerOrConsultantPermission'
]

timezone = TIME_ZONE
CELERY_BROKER_POOL_LIMIT = config("CELERY_BROKER_POOL_LIMIT", cast=int, default=1)
CELERY_BROKER_CONNECTION_TIMEOUT = config(
    "CELERY_BROKER_CONNECTION_TIMEOUT", cast=float, default=30.0
)

event_queue_ttl = config("CELERY_EVENT_QUEUE_TTL", cast=float, default=5.0)

accept_content = ['application/json']
task_serializer = 'json'
result_serializer = 'json'
redis_max_connections = 30
worker_max_tasks_per_child = 1000
broker_url = 'memory://' if ENV_DEV else celery_url
broker_connection_retry_on_startup = True
task_always_eager = ENV_DEV
task_eager_propagates = ENV_DEV

result_extended = True
cache_backend = 'redis'
result_backend = 'django-db'

PRIORITY_QUEUE = 'PRIORITY_QUEUE'
SINGLE_QUEUE_EXCEL = 'SINGLE_QUEUE_EXCEL'
DEFAULT_QUEUE_EXCEL = SINGLE_QUEUE_EXCEL
SINGLE_QUEUE_EXCEL_CONCURRENCY = config('SINGLE_QUEUE_EXCEL_CONCURRENCY', cast=int, default=1)

queues = ['QUEUE_CELERY_VOXUM_PROCESS_FILE', PRIORITY_QUEUE]

QUEUE_CELERY_VOXUM = 'QUEUE_CELERY_VOXUM'

task_default_queue = QUEUE_CELERY_VOXUM
default_exchange = Exchange(QUEUE_CELERY_VOXUM, type='direct')


class CustomQueue(Queue):

    def __init__(self, name='', exchange=None, routing_key='',
                 channel=None, bindings=None, on_declared=None, concurrency=None, **kwargs):
        super().__init__(name=name, exchange=exchange, routing_key=routing_key,
                         channel=channel, bindings=bindings, on_declared=on_declared, **kwargs)
        self.concurrency = concurrency


task_queues_list = [
    CustomQueue(QUEUE_CELERY_VOXUM, exchange=default_exchange, routing_key=QUEUE_CELERY_VOXUM),
    CustomQueue(SINGLE_QUEUE_EXCEL, exchange=default_exchange, routing_key=SINGLE_QUEUE_EXCEL,
                concurrency=SINGLE_QUEUE_EXCEL_CONCURRENCY),
]

for queue in queues:
    task_queues_list.append(CustomQueue(queue, exchange=Exchange(queue, type='direct'), routing_key=queue))

task_queues = task_queues_list

DATA_UPLOAD_MAX_NUMBER_FIELDS = 6000
CELERY_LOG_LEVEL = 'INFO'
CELERY_PROCESS_QUEUE = 'QUEUE_CELERY_VOXUM_PROCESS_FILE'

REDIS_PASSWORD = config('REDIS_PASSWORD', cast=str, default='')
CIAM_BASE_URL = config('BASE_URL_CIAM', cast=str, default='')
CIAM_ACCESS_TOKEN = config('ACCESS_TOKEN_CIAM', cast=str, default='')
VOTING_RESULT_CH = 'voting_result_guest'

MSAL_CIAM_CLIENT_ID = config('MSAL_CIAM_CLIENT_ID', cast=str, default='')
MSAL_CIAM_CLIENT_SECRET = config('MSAL_CIAM_CLIENT_SECRET', cast=str, default='')
MSAL_CIAM_TENANT = config('MSAL_CIAM_TENANT', cast=str, default='')
MSAL_CIAM_CIAM_RESOURCE = config('MSAL_CIAM_CIAM_RESOURCE', cast=str, default='')
MSAL_CIAM_GRANT_TYPE = config('MSAL_CIAM_GRANT_TYPE', cast=str, default='')
MSAL_CIAM_ORGANIZATION = config('MSAL_CIAM_ORGANIZATION', cast=str, default='')
MSAL_CIAM_USER_ID = config('MSAL_CIAM_USER_ID', cast=str, default='')
MSAL_CIAM_ROLES = config('MSAL_CIAM_ROLES', cast=str, default='USERROLE').split(',')
guest_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'apps', 'guest', 'templates',
                          'emails')

body_content_send_ciam_link = os.path.join(guest_path, 'send_ciam_link.html')
body_content_send_meeting_link = os.path.join(guest_path, 'send_meeting_link.html')

CIAM_CONFIGURATION = {
    "url_login": f'https://login.microsoftonline.com/{MSAL_CIAM_TENANT}/oauth2/v2.0/token',
    "client_id": MSAL_CIAM_CLIENT_ID,
    "client_secret": MSAL_CIAM_CLIENT_SECRET,
    "tenant": MSAL_CIAM_TENANT,
    "grant_type": MSAL_CIAM_GRANT_TYPE,
    "resource": MSAL_CIAM_CIAM_RESOURCE,
    "user_type": 'external',
    "ciam": {
        "organization": MSAL_CIAM_ORGANIZATION,
        "roles": MSAL_CIAM_ROLES,
        "initiated_by": MSAL_CIAM_USER_ID,
        "preferred_language": "Pt",
        "inline": True,
        "send_email": False,
        "user_id": MSAL_CIAM_USER_ID,
        "body_content": body_content_send_ciam_link,
        "body_content_send_meeting_link": body_content_send_meeting_link,
        "application_name": APP_NAME,
        "action": "Cadastrar",
        "subject": 'Link de Cadastro do Usuário',
        "pre_header_content": 'Link de Cadastro do Usuário',
    }
}

REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = (
    "config.renderer.VoxumAPIRendererInterceptor",
    "rest_framework.renderers.BrowsableAPIRenderer",)
task_track_started = True
result_persistent = True

GUEST_USER_MODEL = 'guest.UserGuest'

WEB_PAGINATOR = config('WEB_PAGINATOR', cast=bool, default=False)

if ENV_DEV:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'voxum-local',
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": channel_redis_cache,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            }
        }
    }

SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"
SESSION_CACHE_ALIAS = "default"