import logging
import os

import requests
from celery_singleton import Singleton

from . import serializers, models
from settings import celery_app

BOT_URL = f'http://{os.environ.get("TELEGRAM_BOT_HOST")}:{os.environ.get("TELEGRAM_BOT_PORT")}'


@celery_app.task()
def notification(user_id, lang, _=None):
    requests.post(
        f'{BOT_URL}/api/send_notification/',
        json={
            'user_id': user_id,
            'lang': lang,
        }
    )


@celery_app.task()
def send_translation():
    langs = models.Language.objects.all()
    serializer = serializers.LanguageSerializer(data=langs, many=True)
    serializer.is_valid()
    requests.post(
        f'{BOT_URL}/api/translation/send/',
        json={
            'data': serializer.data,
        }
    )

@celery_app.task()
def clear_user_cache(user_id, _=None):
    requests.post(
        f'{BOT_URL}/api/user/clearcache/{user_id}/'
    )