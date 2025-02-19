import django
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.models import AnonymousUser



class GroupChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Get the room id from the URL route
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        # Construct a group name, e.g., "chat_room_room123"
        self.room_group_name = f'chat_room_{self.room_id}'

        # Join the group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group on disconnect
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        username = data.get('username', 'Anonymous')

        # Broadcast message to the group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
            }
        )

    async def chat_message(self, event):
        # Send the message to WebSocket clients
        await self.send(text_data=json.dumps({
            'username': event.get('username', 'Anonymous'),
            'message': event['message']
        }))
