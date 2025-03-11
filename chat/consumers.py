import django
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message 
from django.contrib.auth.models import AnonymousUser

import json
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import UntypedToken
from chat.models import ChatRoom  # your ChatRoom model
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
import re



User = get_user_model()

class MultiplexChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Handle WebSocket connection and authenticate users"""
        print("🔵 WebSocket connection attempt received...")

        user = self.scope.get("user", AnonymousUser())

        if not user.is_authenticated:
            token = self.get_token_from_query(self.scope["query_string"].decode())
            print(f"🔑 Extracted Token: {token}")

            if token:
                user = await self.jwt_get_user(token)  # Authenticate via JWT
                self.scope["user"] = user  # Store user in scope

        if not user.is_authenticated:
            print("❌ WebSocket Authentication Failed. Closing Connection.")
            await self.close()
            return

        self.user = user
        self.rooms = set()

        print(f"✅ User authenticated: {user.username}")

        # Accept WebSocket connection
        await self.accept()

        # ✅ **Join ALL chat rooms, including new ones**
        user_rooms = await self.get_user_rooms_with_last_message(user)
        for room in user_rooms:
            group_name = f"chat_{room['id']}"
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.rooms.add(group_name)

        # ✅ **Also subscribe to a global notification group**
        await self.channel_layer.group_add("global_notifications", self.channel_name)

        # Send the list of rooms to the connected user
        await self.send(json.dumps({
            "action": "room_list",
            "rooms": user_rooms
        }))

         # **Send missed messages count**
        missed_messages = await self.get_missed_messages_count(user)
        print(f"📌 Missed Messages Count: {missed_messages}")

        # Notify user of missed messages count
        await self.send(json.dumps({
            "action": "missed_messages",
            "missed_messages": missed_messages
        }))

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection and remove user from groups"""
        print(f"🔴 WebSocket Disconnected for {self.user.username}")

        for group in list(self.rooms):
            await self.channel_layer.group_discard(group, self.channel_name)

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        if not text_data.strip():  # Handle empty messages
            print("⚠️ Received an empty WebSocket message. Ignoring.")
            return

        try:
            data = json.loads(text_data)
            action = data.get("action")
            user = self.scope.get("user", AnonymousUser())

            if action == "join":
                await self.join_room(data, user)

            elif action == "leave":
                await self.leave_room(data)

            elif action == "load_messages":
                await self.load_messages(data)

            elif action == "send":
                await self.send_message(data, user)
                
            else:
                await self.send(json.dumps({"error": "Unknown action"}))
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON message received: {text_data}. Error: {e}")
            await self.send(json.dumps({"error": "Invalid message format"}))

    async def join_room(self, data, user):
        """Join a chat room"""
        room_id = data.get("room")
        if room_id and await self.check_membership(room_id, user):
            group_name = f"chat_{room_id}"
            if group_name not in self.rooms:
                await self.channel_layer.group_add(group_name, self.channel_name)
                self.rooms.add(group_name)
            await self.send(json.dumps({
                "action": "joined",
                "room": room_id,
                "message": f"Joined room {room_id}"
            }))
        else:
            await self.send(json.dumps({
                "action": "error",
                "message": f"You are not a member of room {room_id}."
            }))

    async def leave_room(self, data):
        """Leave a chat room"""
        room_id = data.get("room")
        if room_id:
            group_name = f"chat_{room_id}"
            await self.channel_layer.group_discard(group_name, self.channel_name)
            self.rooms.discard(group_name)
            await self.send(json.dumps({
                "action": "left",
                "room": room_id,
                "message": f"Left room {room_id}"
            }))

    async def load_messages(self, data):
        """Load paginated chat messages"""
        room_id = data.get("room_id")
        page = int(data.get("page", 1))
         # Fetch messages
        messages = await self.get_chat_messages(room_id, page)

        # Mark messages as read
        await self.mark_messages_as_read(room_id, self.user)

        await self.send(json.dumps({
            "action": "message_list",
            "room_id": room_id,
            "messages": messages
        }))

    async def send_message(self, data, user):
        """Securely send a message to a chat room"""
        
        # Ensure user is authenticated
        if user.is_anonymous:
            await self.send(json.dumps({
                "action": "error",
                "message": "Authentication required to send messages."
            }))
            return

        # Extract message details
        room_id = data.get("room_id")
        message_text = data.get("message", "").strip()  # Ensures no empty messages

        # Validate inputs
        if not room_id or not message_text:
            await self.send(json.dumps({
                "action": "error",
                "message": "Invalid room or empty message."
            }))
            return

        # Check if the user is a member of the room
        is_member = await self.check_membership(room_id, user)
        if not is_member:
            await self.send(json.dumps({
                "action": "error",
                "message": "You are not a member of this chat room."
            }))
            return

        # Sanitize message content (Prevent XSS or Injection)
        message_text = re.sub(r'[<>]', '', message_text)  # Remove HTML tags

        # Save the message securely in the database
        message = await self.save_message(room_id, user, message_text)

        # Broadcast message to the chat room
        group_name = f"chat_{room_id}"
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "chat_message",
                "room_id": room_id,
                "username": user.username,
                "sender": user.username,
                "message": message_text,
                "timestamp": message["timestamp"]
            }
        )

        # Notify all users in the chat room about missed messages
        await self.notify_missed_messages(room_id)

    async def chat_message(self, event):
        """Broadcast chat messages to room members"""
        await self.send(json.dumps({
            "action": "message",
            "room": event.get("room_id"),
            "username": event.get("username"),
            "sender": event.get("sender"),
            "message": event.get("message"),
            "timestamp": event.get("timestamp"),
           
        }))

    async def notify_new_room(self, event):
        """Notify user and auto-subscribe them to new rooms."""
        print(f"🔔 WebSocket received new room notification: {event}")

        room_id = event["room"]["id"]
        group_name = f"chat_{room_id}"

        if group_name not in self.rooms:
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.rooms.add(group_name)

        result = []
        result.append(event["room"])
        print(event["room"])
        await self.send(json.dumps({
            "action": "new_room",
            "rooms": result,
        }))


    def get_token_from_query(self, query_string):
        """Extract Bearer token from WebSocket query params"""
        query_params = dict(qc.split("=") for qc in query_string.split("&") if "=" in qc)
        token = query_params.get("Bearertoken", "").strip()
        if not token:
            print("❌ No token found in WebSocket URL")
        return token or None

    @database_sync_to_async
    def jwt_get_user(self, token):
        """Validate JWT token and retrieve the user"""
        try:
            print(f"🔑 Authenticating token: {token}")
            decoded_token = AccessToken(token)  # Validate JWT
            user = User.objects.get(id=decoded_token["user_id"])
            print(f"✅ Authenticated user: {user.username}")
            return user
        except Exception as e:
            print(f"❌ JWT Authentication failed: {e}")
            return AnonymousUser()

    @database_sync_to_async
    def check_membership(self, room_id, user):
        """Check if user is a member of the room"""
        try:
            room = ChatRoom.objects.get(id=room_id)
            return room.members.filter(id=user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    @database_sync_to_async
    def get_user_rooms_with_last_message(self, user):
        """Fetch user's chat rooms along with the last message"""
        rooms = ChatRoom.objects.filter(members=user).prefetch_related("messages")
        result = []
        for room in rooms:
            last_message = room.messages.order_by("-timestamp").first()
            result.append({
                "id": room.id,
                "name": room.name,
                "last_message": last_message.content if last_message else "No messages yet",
                "last_message_time": last_message.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_message else "",
            })
        return result

    @database_sync_to_async
    def get_chat_messages(self, room_id, page):
        """Retrieve paginated chat messages"""
        PAGE_SIZE = 20
        offset = (page - 1) * PAGE_SIZE
        messages = Message.objects.filter(room_id=room_id).order_by("-timestamp")[offset:offset + PAGE_SIZE]

        return [{"username": msg.sender.username, "message": msg.content, "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for msg in messages]

    @database_sync_to_async
    def save_message(self, room_id, user, text):
        """Save chat messages to the database"""
        room = ChatRoom.objects.get(id=room_id)
        message = Message.objects.create(room=room, sender=user, content=text)
        return {"message": message.content, "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

    @database_sync_to_async
    def get_missed_messages_count(self, user):
        """Get the number of unread messages per chat room for a user"""
        rooms = ChatRoom.objects.filter(members=user)
        missed_messages = {}

        for room in rooms:
            unread_count = room.messages.exclude(read_by=user).count()
            if unread_count > 0:
                missed_messages[room.id] = unread_count  # Store count per room

        return missed_messages
    
    @database_sync_to_async
    def mark_messages_as_read(self, room_id, user):
        """Mark all unread messages in a room as read by the user"""
        room = ChatRoom.objects.get(id=room_id)
        unread_messages = room.messages.exclude(read_by=user)
        
        for message in unread_messages:
            message.read_by.add(user)  # Mark as read



