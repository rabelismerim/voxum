import redis

from celery import Celery
from config import settings

app = Celery('config')
app.config_from_object(settings)
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

passwd = settings.REDIS_PASSWORD

if passwd:
    REDIS_CONN = redis.from_url(settings.celery_url, password=settings.REDIS_PASSWORD)
else:
    REDIS_CONN = redis.from_url(settings.celery_url)
