import logging
import os

from celery import Celery


# Установите переменную окружения для настройки Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.settings")

app = Celery("backend")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()