#region redis consumer implementation
# import django
# django.setup()
# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from .models import ChatRoom, Message 
# from django.contrib.auth.models import AnonymousUser

# import json
# import jwt
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.conf import settings
# from django.contrib.auth.models import AnonymousUser
# from rest_framework_simplejwt.tokens import UntypedToken
# from chat.models import ChatRoom  # your ChatRoom model
# from django.contrib.auth import get_user_model
# from rest_framework_simplejwt.tokens import AccessToken
# from asgiref.sync import sync_to_async
# import re
# import os
# from decouple import config
# import ssl



# import redis
# from asgiref.sync import sync_to_async

# # ADDED: Initialize a global Redis client
# REDIS_URL = config("REDIS_TLS_URL")

# redis_client = redis.Redis.from_url(
#     REDIS_URL,
#     decode_responses=True,
#     ssl_cert_reqs=ssl.CERT_NONE  # <-- Fix SSL certificate error
# )


# User = get_user_model()


# @sync_to_async
# def set_user_online(user_id: int):
#     """Mark user as 'online' in Redis."""
#     redis_client.set(f"user_status:{user_id}", "online", ex=3600)
#     # The 'ex=3600' means it'll expire in 1 hour if not updated.
#     # You can omit ex=... or choose a different time.

# @sync_to_async
# def set_user_offline(user_id: int):
#     """Mark user as 'offline' in Redis."""
#     redis_client.set(f"user_status:{user_id}", "offline")


# @sync_to_async
# def is_user_offline(user_id: int) -> bool:
#     """Check if user is offline in Redis."""
#     status = redis_client.get(f"user_status:{user_id}")
    
#     if not status:
#         # Key doesn't exist or expired; treat as offline
#         return True
    
#     return status == "offline" 


# @sync_to_async
# def store_offline_in_redis(recipient_id: int, message_data: dict):
#     """
#     Stores a message for an offline user in a Redis list.
#     We'll use LPUSH or RPUSH. 
#     Let's pick LPUSH => So we can RPOP later in get_offline_messages if we want.
#     """
#     key = f"offline_messages:{recipient_id}"
#     redis_client.lpush(key, json.dumps(message_data))
#     # Optionally set an expire, e.g. redis_client.expire(key, 604800)  # 7 days


# @sync_to_async
# def get_offline_messages(user_id: int):
#     """
#     Pop all offline messages from Redis list offline_messages:{user_id}.
#     Return them as a list of dicts.
#     """
#     key = f"offline_messages:{user_id}"
#     messages = []

#     # We'll do RPOP in a while loop, since we did LPUSH earlier
#     # Or you can do LRANGE + LTRIM if you prefer.
#     while True:
#         raw = redis_client.rpop(key)
#         if not raw:
#             break
#         messages.append(json.loads(raw))

#     # The messages are now in reverse order (if we use RPOP after LPUSH).
#     # So we might want to reverse them to keep chronological sequence:
#     messages.reverse()
#     return messages


# class MultiplexChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         """Handle WebSocket connection and authenticate users"""
#         print("🔵 WebSocket connection attempt received...")

#         user = self.scope.get("user", AnonymousUser())

#         if not user.is_authenticated:
#             token = self.get_token_from_query(self.scope["query_string"].decode())
#             print(f"🔑 Extracted Token: {token}")

#             if token:
#                 user = await self.jwt_get_user(token)  # Authenticate via JWT
#                 self.scope["user"] = user  # Store user in scope

#         if not user.is_authenticated:
#             print("❌ WebSocket Authentication Failed. Closing Connection.")
#             await self.close()
#             return

#         self.user = user
#         self.rooms = set()

#         print(f"✅ User authenticated: {user.username}")

#         # Mark user as online in Redis
#         await set_user_online(self.user.id)


#         # Accept WebSocket connection
#         await self.accept()


#         offline_msgs = await get_offline_messages(self.user.id)
#         if offline_msgs:
#             await self.send(json.dumps({
#                 "action": "offline_messages",
#                 "messages": offline_msgs
#             }))

#         # Join ALL chat rooms, including new ones**
#         user_rooms = await self.get_user_rooms_with_last_message(user)
#         for room in user_rooms:
#             group_name = f"chat_{room['id']}"
#             await self.channel_layer.group_add(group_name, self.channel_name)
#             self.rooms.add(group_name)

#         # Also subscribe to a global notification group**
#         await self.channel_layer.group_add("global_notifications", self.channel_name)

#         # Send the list of rooms to the connected user
#         await self.send(json.dumps({
#             "action": "room_list",
#             "rooms": user_rooms
#         }))

#          # Send missed messages count
#         missed_messages = await self.get_missed_messages_count(user)
#         print(f"📌 Missed Messages Count: {missed_messages}")
#         await self.send(json.dumps({
#             "action": "missed_messages",
#             "missed_messages": missed_messages
#         }))

#     async def disconnect(self, close_code):
#         """Handle WebSocket disconnection and remove user from groups"""
#         print(f"🔴 WebSocket Disconnected for {self.user.username}")

#         # Mark user as offline in Redis
#         await set_user_offline(self.user.id)

#         for group in list(self.rooms):
#             await self.channel_layer.group_discard(group, self.channel_name)

#     async def receive(self, text_data):
#         """Handle incoming WebSocket messages"""
#         if not text_data.strip():  # Handle empty messages
#             print("⚠️ Received an empty WebSocket message. Ignoring.")
#             return

#         try:
#             data = json.loads(text_data)
#             action = data.get("action")
#             user = self.scope.get("user", AnonymousUser())

#             if action == "join":
#                 await self.join_room(data, user)

#             elif action == "leave":
#                 await self.leave_room(data)

#             elif action == "load_messages":
#                 await self.load_messages(data)

#             elif action == "send":
#                 await self.send_message(data, user)
                
#             else:
#                 await self.send(json.dumps({"error": "Unknown action"}))
#         except json.JSONDecodeError as e:
#             print(f"❌ Invalid JSON message received: {text_data}. Error: {e}")
#             await self.send(json.dumps({"error": "Invalid message format"}))

#     async def join_room(self, data, user):
#         """Join a chat room"""
#         room_id = data.get("room")
#         if room_id and await self.check_membership(room_id, user):
#             group_name = f"chat_{room_id}"
#             if group_name not in self.rooms:
#                 await self.channel_layer.group_add(group_name, self.channel_name)
#                 self.rooms.add(group_name)
#             await self.send(json.dumps({
#                 "action": "joined",
#                 "room": room_id,
#                 "message": f"Joined room {room_id}"
#             }))
#         else:
#             await self.send(json.dumps({
#                 "action": "error",
#                 "message": f"You are not a member of room {room_id}."
#             }))

#     async def leave_room(self, data):
#         """Leave a chat room"""
#         room_id = data.get("room")
#         if room_id:
#             group_name = f"chat_{room_id}"
#             await self.channel_layer.group_discard(group_name, self.channel_name)
#             self.rooms.discard(group_name)
#             await self.send(json.dumps({
#                 "action": "left",
#                 "room": room_id,
#                 "message": f"Left room {room_id}"
#             }))

#     async def load_messages(self, data):
#         """Load paginated chat messages"""
#         room_id = data.get("room_id")
#         page = int(data.get("page", 1))
#          # Fetch messages
#         messages = await self.get_chat_messages(room_id, page)

#         # Mark messages as read
#         await self.mark_messages_as_read(room_id, self.user)

#         await self.send(json.dumps({
#             "action": "message_list",
#             "room_id": room_id,
#             "messages": messages
#         }))

#     async def store_offline_for_room_members(self, room_id, sender, msg_data):
#             members = await self.get_room_members(room_id)
#             for member_id in members:
#                 if member_id != sender.id:
#                     offline = await is_user_offline(member_id)  # is_user_offline is @sync_to_async
#                     if offline:
#                         message_payload = {
#                             "room_id": room_id,
#                             "sender_id": sender.id,
#                             "sender_username": sender.username,
#                             "content": msg_data["message"],
#                             "timestamp": msg_data["timestamp"]
#                         }
#                         await store_offline_in_redis(member_id, message_payload)  
#                         # store_offline_in_redis is also @sync_to_async


    
#     async def send_message(self, data, user):
#         """Securely send a message to a chat room"""
        
#         # Ensure user is authenticated
#         if user.is_anonymous:
#             await self.send(json.dumps({
#                 "action": "error",
#                 "message": "Authentication required to send messages."
#             }))
#             return

#         # Extract message details
#         room_id = data.get("room_id")
#         message_text = data.get("message", "").strip()  # Ensures no empty messages

#         # Validate inputs
#         if not room_id or not message_text:
#             await self.send(json.dumps({
#                 "action": "error",
#                 "message": "Invalid room or empty message."
#             }))
#             return

#         # Check if the user is a member of the room
#         is_member = await self.check_membership(room_id, user)
#         if not is_member:
#             await self.send(json.dumps({
#                 "action": "error",
#                 "message": "You are not a member of this chat room."
#             }))
#             return

#         # Sanitize message content (Prevent XSS or Injection)
#         message_text = re.sub(r'[<>]', '', message_text)  # Remove HTML tags

#         # Save the message securely in the database
#         message = await self.save_message(room_id, user, message_text)

#         # Broadcast message to the chat room
#         group_name = f"chat_{room_id}"
#         await self.channel_layer.group_send(
#             group_name,
#             {
#                 "type": "chat_message",
#                 "room_id": room_id,
#                 "username": user.username,
#                 "sender": user.username,
#                 "message": message_text,
#                 "timestamp": message["timestamp"]
#             }
#         )

#         # Store the message in Redis for all offline members, fetch all members except the sender, then check if they're offline
#         await self.store_offline_for_room_members(room_id, user, message)

#         # Notify about missed messages, if you still want that logic
#         await self.notify_missed_messages(room_id)

#     async def chat_message(self, event):
#         """Broadcast chat messages to room members"""
#         await self.send(json.dumps({
#             "action": "message",
#             "room": event.get("room_id"),
#             "username": event.get("username"),
#             "sender": event.get("sender"),
#             "message": event.get("message"),
#             "timestamp": event.get("timestamp"),
           
#         }))

#     async def notify_new_room(self, event):
#         """Notify user and auto-subscribe them to new rooms."""
#         print(f"🔔 WebSocket received new room notification: {event}")

#         room_id = event["room"]["id"]
#         group_name = f"chat_{room_id}"

#         if group_name not in self.rooms:
#             await self.channel_layer.group_add(group_name, self.channel_name)
#             self.rooms.add(group_name)

#         result = []
#         result.append(event["room"])
#         print(event["room"])
#         await self.send(json.dumps({
#             "action": "new_room",
#             "rooms": result,
#         }))


#     def get_token_from_query(self, query_string):
#         """Extract Bearer token from WebSocket query params"""
#         query_params = dict(qc.split("=") for qc in query_string.split("&") if "=" in qc)
#         token = query_params.get("Bearertoken", "").strip()
#         if not token:
#             print("❌ No token found in WebSocket URL")
#         return token or None

#     @database_sync_to_async
#     def jwt_get_user(self, token):
#         """Validate JWT token and retrieve the user"""
#         try:
#             print(f"🔑 Authenticating token: {token}")
#             decoded_token = AccessToken(token)  # Validate JWT
#             user = User.objects.get(id=decoded_token["user_id"])
#             print(f"✅ Authenticated user: {user.username}")
#             return user
#         except Exception as e:
#             print(f"❌ JWT Authentication failed: {e}")
#             return AnonymousUser()

#     @database_sync_to_async
#     def check_membership(self, room_id, user):
#         """Check if user is a member of the room"""
#         try:
#             room = ChatRoom.objects.get(id=room_id)
#             return room.members.filter(id=user.id).exists()
#         except ChatRoom.DoesNotExist:
#             return False

#     @database_sync_to_async
#     def get_user_rooms_with_last_message(self, user):
#         """Fetch user's chat rooms along with the last message"""
#         rooms = ChatRoom.objects.filter(members=user).prefetch_related("messages")
#         result = []
#         for room in rooms:
#             last_message = room.messages.order_by("-timestamp").first()
#             result.append({
#                 "id": room.id,
#                 "name": room.name,
#                 "last_message": last_message.content if last_message else "No messages yet",
#                 "last_message_time": last_message.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_message else "",
#             })
#         return result

#     @database_sync_to_async
#     def get_chat_messages(self, room_id, page):
#         """Retrieve paginated chat messages"""
#         PAGE_SIZE = 20
#         offset = (page - 1) * PAGE_SIZE
#         messages = Message.objects.filter(room_id=room_id).order_by("-timestamp")[offset:offset + PAGE_SIZE]

#         return [{"username": msg.sender.username, "message": msg.content, "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for msg in messages]

#     @database_sync_to_async
#     def save_message(self, room_id, user, text):
#         """Save chat messages to the database"""
#         room = ChatRoom.objects.get(id=room_id)
#         message = Message.objects.create(room=room, sender=user, content=text)
#         return {"message": message.content, "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

#     @database_sync_to_async
#     def get_missed_messages_count(self, user):
#         """Get the number of unread messages per chat room for a user"""
#         rooms = ChatRoom.objects.filter(members=user)
#         missed_messages = {}

#         for room in rooms:
#             unread_count = room.messages.exclude(read_by=user).count()
#             if unread_count > 0:
#                 missed_messages[room.id] = unread_count  # Store count per room

#         return missed_messages
    
#     @database_sync_to_async
#     def mark_messages_as_read(self, room_id, user):
#         """Mark all unread messages in a room as read by the user"""
#         room = ChatRoom.objects.get(id=room_id)
#         unread_messages = room.messages.exclude(read_by=user)
        
#         for message in unread_messages:
#             message.read_by.add(user)  # Mark as read


#     @database_sync_to_async
#     def get_room_members(self, room_id):
#         """Return a list of user IDs for all members of a room."""
#         room = ChatRoom.objects.get(id=room_id)
#         return list(room.members.values_list("id", flat=True))


#endregion


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
from chat.models import ChatRoom
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from asgiref.sync import sync_to_async
import re
from main.models import Media

import redis
from decouple import config
import ssl
from .models import RoomMembership

# Initialize a global Redis client
REDIS_URL = config("REDIS_TLS_URL")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    ssl_cert_reqs=ssl.CERT_NONE,
    # ssl_cert_reqs=None
)





User = get_user_model()

@sync_to_async
def set_user_online(user_id: int):
    """Mark user as online with optional TTL to auto-expire."""
    redis_client.set(f"user_status:{user_id}", "online", ex=3600)


@sync_to_async
def set_user_offline(user_id: int):
    redis_client.set(f"user_status:{user_id}", "offline")

@sync_to_async
def is_user_offline(user_id: int) -> bool:
    status = redis_client.get(f"user_status:{user_id}")
    if not status:
        # If key is missing or expired, treat as offline
        return True
    return (status.decode() == "offline")

@sync_to_async
def increment_unread_count(user_id: int, room_id: int):
    """Increment unread count in a Redis hash for that user."""
    redis_client.hincrby(f"unread_counts:{user_id}", str(room_id), 1)

@sync_to_async
def reset_unread_count(user_id: int, room_id: int):
    """Reset unread count to 0 for that user-room."""
    redis_client.hset(f"unread_counts:{user_id}", str(room_id), 0)

@sync_to_async
def get_unread_count(user_id: int, room_id: int) -> int:
    """Get the current unread count for a user-room pair."""
    val = redis_client.hget(f"unread_counts:{user_id}", str(room_id))
    return int(val) if val else 0


class MultiplexChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        """Handle WebSocket connection and authenticate users"""
        print("🔵 WebSocket connection attempt received...")
        self.rooms = set()

        # Authenticate and connect user
        user = self.scope.get("user", AnonymousUser())

        if not user.is_authenticated:
            token = self.get_token_from_query(self.scope["query_string"].decode())

            if token:
                user = await self.jwt_get_user(token)  # Authenticate via JWT
                self.scope["user"] = user  # Store user in scope

        if not user.is_authenticated:
            print("❌ WebSocket Authentication Failed. Closing Connection.")
            await self.close()
            return

        self.user = user
        

         # Mark user online in Redis
        await set_user_online(self.user.id)

        # Accept WebSocket connection
        await self.accept()


        # Join ALL chat rooms, including new ones
        missed_messages = []
        user_rooms = await self.get_user_rooms_with_last_message(user)
        for room in user_rooms:
            group_name = f"chat_{room['id']}"
            # Send missed messages count**
            # fetch offline unread message count
            missed_messages_details = await get_unread_count(self.user.id, room['id'])
            missed_messages.append({room['id']: missed_messages_details})
            print(missed_messages)
            # missed_messages = await self.get_missed_messages_count(user)
            await self.channel_layer.group_add(group_name, self.channel_name)
            self.rooms.add(group_name)

        print(f"Missed Messages Count: {missed_messages}")

        print("user_rooms",user_rooms)

        # Also subscribe to a global notification group**
        await self.channel_layer.group_add("global_notifications", self.channel_name)

        # Send the list of rooms to the connected user
        await self.send(json.dumps({
            "action": "room_list",
            "rooms": user_rooms
        }))

         

        # Notify user of missed messages count
        await self.send(json.dumps({
            "action": "missed_messages",
            "missed_messages": missed_messages
        }))


    async def disconnect(self, close_code):
        """Handle WebSocket disconnection and remove user from groups"""
        print(f"🔴 WebSocket Disconnected. Close Code: {close_code}")
        if hasattr(self, "rooms"):
            for group in list(self.rooms):
                await self.channel_layer.group_discard(group, self.channel_name)

        # Only mark the user offline if self.user exists.
        if hasattr(self, "user") and getattr(self.user, "id", None):
            await set_user_offline(self.user.id)

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

            elif action == "delete":
                await self.delete_message(data, user)

            elif action == "typing":
                await self.handle_typing(data, user)

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

    async def handle_typing(self, data, user):
        """Broadcast typing status to others in the same room."""
        if user.is_anonymous:
            await self.send(json.dumps({
                "action": "error",
                "message": "Authentication required to send typing events."
            }))
            return

        room_id = data.get("room_id")
        typing = data.get("typing", False)  # a boolean: True if typing, False if stopped

        # Optional: check if user is actually a member
        is_member = await self.check_membership(room_id, user)
        if not is_member:
            await self.send(json.dumps({
                "action": "error",
                "message": "You are not a member of this chat room."
            }))
            return

        # Broadcast to the room's group
        group_name = f"chat_{room_id}"
        await self.channel_layer.group_send(
                group_name,
            {
                "type": "typing_event",
                "room_id": room_id,
                "username": user.username,
                "typing": typing
            }
        )


    async def typing_event(self, event):
        """
        event = {
            "type": "typing_event",
            "room_id": ...,
            "username": ...,
            "typing": bool
        }
        """
        print("pooo")
        await self.send(json.dumps({
            "action": "typing",
            "room": event["room_id"],
            "username": event["username"],
            "typing": event["typing"],
        }))


    async def load_messages(self, data):
        """Load paginated chat messages"""
        room_id = data.get("room_id")
        page = int(data.get("page", 1))
         # Fetch messages
        messages = await self.get_chat_messages(room_id, page)

        print("")
        print("messages", messages)

        # Mark messages as read
        await self.mark_messages_as_read(room_id, self.user)


        # reset redis message count
        if messages:
            newest_ts = messages[0]["timestamp"] 
            await self.update_last_read(room_id, self.user, newest_ts)

        # Reset unread count in Redis
        await reset_unread_count(self.user.id, room_id)


         # Fetch room members
        members = await self.get_room_members(room_id)

        await self.send(json.dumps({
            "action": "message_list",
            "room_id": room_id,
            "messages": messages,
            "members": members,
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
        media_list = data.get("media", [])

        if not room_id or (not message_text and not media_list):
            await self.send(json.dumps({"action": "error", "message": "Invalid message"}))
            return

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

        print("")
        print("dtaa", data)

        # Attemptong to find the original message if reply_to_id is provided
        reply_to_id = data.get("reply_to_id")
        

        reply_to_msg = None
        if reply_to_id:
            try:
                reply_to_msg = await database_sync_to_async(Message.objects.get)(id=reply_to_id)
                print("async", reply_to_msg)
            except Message.DoesNotExist:
                reply_to_msg = None

        # Save the message securely in the database
        message = await self.save_message(room_id, user, message_text, reply_to_id, reply_to_msg)
        # getting the reply message sender
        sender_username = None
        if reply_to_msg:
            sender_username = await sync_to_async(lambda: reply_to_msg.sender.username)()
        # Save media files
        if media_list:
            await self.save_media(message, media_list)


        print("")
        print(message)
        print("babe")
        print(reply_to_id, reply_to_msg)

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
                "media": media_list,
                "timestamp": message["timestamp"],
                "reply_to_id": reply_to_id,
                "reply_to_content": str(reply_to_msg),
                "reply_message_sender":sender_username,
                "message_id" : message['id'],
                
            }
        )

        # Notify all users in the chat room about missed messages
        # await self.notify_missed_messages(room_id)

        # increment unread messages in redis
        await increment_unread_count(self.user.id, room_id)



    # async def notify_missed_messages(self, room_id):
    #     """
    #     Compute the missed/unread messages for each member of the given room,
    #     then broadcast that info so each user can be updated on their own unread counts.
    #     """
    #     # 1) Get the room and its members
    #     room = await database_sync_to_async(ChatRoom.objects.get)(id=room_id)
    #     members = await database_sync_to_async(lambda: list(room.members.all()))()

    #     # 2) For each member, get that member's overall missed messages (across all rooms)
    #     for member in members:
    #         missed_messages = await self.get_missed_messages_count(member)

    #         # 3) Broadcast to the global_notifications group. 
    #         #    All users in that group (which should be everyone) will receive it, 
    #         #    but only the user whose ID matches will actually handle it.
    #         await self.channel_layer.group_send(
    #             "global_notifications",
    #             {
    #                 "type": "missed_messages_notification",
    #                 "user_id": member.id,
    #                 "missed_messages": missed_messages
    #             }
    #         )



    # async def missed_messages_notification(self, event):
    #     """
    #     Handle broadcasted missed_messages_notification. 
    #     Only send to the user whose user_id matches the event.
    #     """
    #     if event["user_id"] == self.user.id:
    #         await self.send(json.dumps({
    #             "action": "missed_messages",
    #             "missed_messages": event["missed_messages"]
    #         }))



    async def chat_message(self, event):
        """Broadcast chat messages to room members"""
        print("")
        print("event", event)
        await self.send(json.dumps({
            "action": "message",
            "room": event.get("room_id"),
            "username": event.get("username"),
            "sender": event.get("sender"),
            "message": event.get("message"),
            "timestamp": event.get("timestamp"),
            "reply_to_id": event.get("reply_to_id"),
            "reply_to_content": event.get("reply_to_content"),
            "message_id": event.get("message_id")
           
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


    
    async def notify_delete_room(self, event):
        """
        event = {
            "type": "notify_delete_room",
            "room": {
                "message": "room deleted"
                ...
            }
        }
        """
        # Send the data over the WebSocket to the client
        await self.send(
            text_data=json.dumps({
                "event": "ROOM_DELETED", 
                "data": event["room"]
            })
        )


    async def delete_message(self, data, user):
        """Mark a message as deleted by replacing its content."""
        message_id = data.get("message_id")

        if not message_id:
            await self.send(json.dumps({
                "action": "error",
                "message": "Message ID is required to delete."
            }))
            return

        # Fetch message and related room in a sync context
        message = await database_sync_to_async(
            lambda: Message.objects.select_related("room").filter(id=message_id, sender=user).first()
        )()

        if not message:
            await self.send(json.dumps({
                "action": "error",
                "message": "Message not found or not authorized to delete."
            }))
            return

        # Update message content to indicate deletion
        message.content = "This message has been deleted."
        message.deleted = True
        await database_sync_to_async(message.save)()  

        # Notify the chat room
        await self.channel_layer.group_send(
            f"chat_{message.room.id}",  # ✅ Now this won't error out
            {
                "type": "message_deleted",
                "message_id": message.id,
                "room_id": message.room.id,
                "username": user.username,
            }
        )

    async def message_deleted(self, event):
        """Send message deleted event to clients."""
        await self.send(json.dumps({
            "action": "message_deleted",
            "message_id": event["message_id"],
            "room_id": event["room_id"],
            "username": event["username"],
        }))


    def get_token_from_query(self, query_string):
        """Extract Bearer token from WebSocket query params"""
        query_params = dict(qc.split("=") for qc in query_string.split("&") if "=" in qc)
        token = query_params.get("Bearertoken", "").strip()
        if not token:
            print("❌ No token found in WebSocket URL")
        return token or None


    @database_sync_to_async
    def get_room_members(self, room_id):
        try:
            room = ChatRoom.objects.get(id=room_id)
            return [{"id": member.id, "username": member.username} for member in room.members.all()]
        except ChatRoom.DoesNotExist:
            return []


    @database_sync_to_async
    def update_last_read(self, room_id, user, newest_timestamp_str):
        """
        Parse newest_timestamp_str to a datetime,
        then update the membership row in the DB.
        """
        from datetime import datetime

        # Parse the string (e.g. "2025-03-10 12:34:56") to a datetime

        format_str = "%Y-%m-%d %H:%M:%S"
        newest_timestamp = datetime.strptime(newest_timestamp_str, format_str)

        print("")
        print("RoomMembership", room_id, user)
        # Query or create the membership
        try:
            membership = RoomMembership.objects.get(room_id=room_id, user=user)
            membership.last_read_at = newest_timestamp
            membership.save()
        except RoomMembership.DoesNotExist:
            # Could log a warning or just pass
            pass

        # Update last_read_at
        membership.last_read_at = newest_timestamp
        membership.save()


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
        # """Fetch user's chat rooms along with the last message from Redis or DB"""
        # cache_key = f"user_rooms:{user.id}"
        
        # # Check Redis for cached rooms
        # cached_rooms = redis_client.get(cache_key)
        # if cached_rooms:
        #     print("✅ Fetching rooms from Redis cache...")
        #     return json.loads(cached_rooms)  # Return cached data as Python list
        
        # print("🔄 Fetching rooms from DB...")

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

        # Cache the result in Redis with a 10-minute expiry
        # redis_client.setex(cache_key, 600, json.dumps(result))  
        return result

    @database_sync_to_async
    def get_chat_messages(self, room_id, page):
        """Retrieve paginated chat messages"""
        PAGE_SIZE = 20
        offset = (page - 1) * PAGE_SIZE
        messages = Message.objects.filter(room_id=room_id).order_by("-timestamp")[offset:offset + PAGE_SIZE]
        return [{"username": msg.sender.username, "id":msg.id, "deleted":msg.deleted, "message": msg.content, "reply_to":str(msg.reply_to),"reply_to_num":msg.reply_to_num, "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")} for msg in messages]


    @database_sync_to_async
    def save_message(self, room_id, user, text, reply_to_num=None, reply_to_msg=None):
        """Save chat messages to the database"""
        print("oversabi", user)
        room = ChatRoom.objects.get(id=room_id)
        message = Message.objects.create(room=room, sender=user, content=text, reply_to_num= reply_to_num, reply_to=reply_to_msg)
          # Exclude the sender from room members for message receivers.
        filtered_receivers  = room.members.exclude(id=user.id)
        message.receiver.add(*filtered_receivers )

         # 🧹 Invalidate Redis Cache (force refetch)
        redis_client.delete(f"user_rooms:{user.id}")

        return {"id": message.id, "message": message.content, "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "reply_to_id": reply_to_msg.id if reply_to_msg else None,}


    @sync_to_async
    def save_media(self, message, media_list):
        """Save media records to DB"""
        Media.objects.bulk_create([
            Media(message=message, url=media["url"], public_id=media["public_id"], media_type=media["type"])
            for media in media_list
        ])


    # @database_sync_to_async
    # def get_missed_messages_count(self, user):
    #     """Get the number of unread messages per chat room for a user"""
    #     rooms = ChatRoom.objects.filter(members=user)
    #     missed_messages = {}

    #     for room in rooms:
    #         unread_count = room.messages.exclude(read_by=user).count()
    #         if unread_count > 0:
    #             missed_messages[room.id] = unread_count  # Store count per room

    #     return missed_messages
    


    @database_sync_to_async
    def mark_messages_as_read(self, room_id, user):
        """Mark all unread messages in a room as read by the user"""
        room = ChatRoom.objects.get(id=room_id)
        unread_messages = room.messages.exclude(read_by=user)
        
        for message in unread_messages:
            message.read_by.add(user)  # Mark as read




