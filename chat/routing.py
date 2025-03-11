# myproject/routing.py
from django.urls import re_path
from .consumers import MultiplexChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/$', MultiplexChatConsumer.as_asgi()),
]