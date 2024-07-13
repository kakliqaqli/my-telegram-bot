from django.urls import path

from settings import consumers
websocket_urlpatterns = [
    path('ws/admin/notifications/', consumers.NotificationConsumer.as_asgi()),
]