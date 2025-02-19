import django
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class GroupChatConsumer(AsyncWebsocketConsumer):
    pass