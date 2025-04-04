import django
django.setup()
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message 
from django.contrib.auth.models import AnonymousUser

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
from main.models import Media, MessageMedia
from main.serializers import MessageMediaSerializer

import redis
from decouple import config
import ssl
from .models import RoomMembership
from django.contrib.contenttypes.models import ContentType
import cloudinary.uploader
from datetime import datetime



# Initialize a global Redis client
REDIS_URL = config("REDIS_TLS_URL")

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    ssl_cert_reqs=ssl.CERT_NONE,
)

USER_TYPE_GROUP_MAP = {
    "HO": "home_owners",
    "CO": "contractors",
    "AG": "agents",
    "IV": "investors",
}



User = get_user_model()

@sync_to_async
def set_user_online(user_id: int):
    """Mark user as online with optional TTL to auto-expire."""
    redis_client.set(f"user_status:{user_id}", "online", ex=60)


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

@database_sync_to_async
def delete_message_media_and_sync_cloudinary(message):
    media_items = list(message.messagemedia.all())
    for media in media_items:
        try:
            cloudinary.uploader.destroy(media.public_id)
        except Exception as e:
            print(f"❌ Cloudinary deletion failed for {media.public_id} — {e}")
    deleted_count, _ = message.messagemedia.all().delete()
    return deleted_count


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
        personal_user_room_id = await self.get_personal_user_rooms_id(user)
        
        get_user_broadcast_rooms = await self.get_or_create_user_broadcast_rooms(user)
        
        print("saviour", get_user_broadcast_rooms)
       
        get_user_broadcast_rooms_for_admin = await self.get_user_broadcast_rooms_for_admin(user)
       
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


        # Also subscribe to a global notification group**
        if self.user.is_superuser:
            await self.channel_layer.group_add("global_notifications", self.channel_name)

        # subscribe users to different broadcast groups
        if not self.user.is_superuser and self.user.user_type:
            USER_TYPE_MAP = {
                "HO": "broadcast_HO",
                "CO": "broadcast_CO",
                "AG": "broadcast_AG",
                "IV": "broadcast_IV"
            }
            await self.channel_layer.group_add(f"{USER_TYPE_MAP[user.user_type]}", self.channel_name)
            print("sub", f"{USER_TYPE_MAP[user.user_type]}")

        # subscribe only the admin to a group
        if self.user.is_superuser:
             await self.channel_layer.group_add("admin_presence", self.channel_name)

        # Send the list of rooms to the connected user
        await self.send(json.dumps({
            "action": "room_list",
            "rooms": user_rooms,
            "broadcast_rooms":get_user_broadcast_rooms_for_admin
        }))

        print("room2")

         

        # Notify user of missed messages count
        await self.send(json.dumps({
            "action": "missed_messages",
            "missed_messages": missed_messages
        }))


        print("room4")

        if personal_user_room_id:
            await self.channel_layer.group_send(
                "admin_presence",
                {
                    "type": "user_status",
                    "user_id": self.user.email,
                    "username": self.user.username,
                    "room_id": personal_user_room_id["room_id"],
                    "room_name": personal_user_room_id["room_name"],
                    "status": "online",
                    "group_room_details":get_user_broadcast_rooms
                }
            )

        print("room5")

    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection and remove user from groups"""
        print(f"🔴 WebSocket Disconnected. Close Code: {close_code}")

        # Remove user from all joined rooms
        if hasattr(self, "rooms"):
            for group in list(self.rooms):
                await self.channel_layer.group_discard(group, self.channel_name)

        # Safely handle user cleanup
        user = getattr(self, "user", None)
        if user and getattr(user, "id", None):
            await set_user_offline(user.id)

            # Remove from admin group if admin
            if user.is_superuser:
                await self.channel_layer.group_discard("admin_presence", self.channel_name)
            else:
                await self.channel_layer.group_send(
                    "admin_presence",
                    {
                        "type": "user_status",
                        "user_id": user.email,
                        "username": user.username,
                        "room_id": None,
                        "room_name": "",
                        "status": "offline"
                    }
                )

        # Cleanup again (just in case)
        if hasattr(self, "rooms"):
            for group in list(self.rooms):
                await self.channel_layer.group_discard(group, self.channel_name)


    # Only admins should receive and see online/offline notifications
    async def user_status(self, event):
        print("status",event)
        if self.user.is_superuser:
            await self.send(json.dumps({
                "action": "user_status",
                "user_id": event["user_id"],
                "username": event["username"],
                "room_name": event["room_name"],
                "room_id": event["room_id"],
                "status": event["status"],
                "group_room_details": event.get("group_room_details", None)
            }))


        print("room6")



    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        if not text_data.strip():  # Handle empty messages
            print("⚠️ Received an empty WebSocket message. Ignoring.")
            return

        try:
            data = json.loads(text_data)
            print("receive", data)
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


            elif action == "load_messages_for_broadcast":
                await self.load_messages_for_agent(data)

            elif action == "send":
                print("scope", user)
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

        # check if user is actually a member
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

        # Mark messages as read
        await self.mark_messages_as_read(room_id, self.user)


        # reset redis message count
        if messages:
            newest_ts = messages[0]["timestamp"] 
            await self.update_last_read(room_id, self.user, newest_ts)

        # Reset unread count in Redis
        await reset_unread_count(self.user.id, room_id)


         # Fetch room members
        room_details = await self.get_room_details(room_id)
        print("")
        print("messages",room_id,room_details )

        user_type = self.user.user_type
        print("gpt",self.user, user_type)

        await self.send(json.dumps({
            "action": "message_list",
            "room_type":room_details["room_type"],
            "room_id": room_id,
            "messages": messages,
            "members": room_details["members"],
            "room_name": room_details["creator"]
            
        }))



    async def load_messages_for_agent(self, data):
        """Load paginated chat messages"""
        room_id = data.get("room_id")
        page = int(data.get("page", 1))
         # Fetch messages
        messages = await self.get_chat_messages(room_id, page)
        if self.user is not None:
            room = await self.get_room_type_for_broadcast(room_id)

        print("")
        print("messages", room.room_type, )


        user_type = self.user.user_type
        print("gpt",self.user, user_type)

        await self.send(json.dumps({
            "action": "message_list_for_broadcast",
            "room_type":room.room_type,
            "room_id": room_id,
            "messages": messages,            
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
        room_type = data.get("room_type")
        print("")
        print("glk", room_type)
        print("")
        message_text = data.get("message", "").strip()  # Ensures no empty messages
        media_list = data.get("media", [])
        broadcast_to = data.get("broadcast_to")  # user type rooms to broadcast to


        if not (room_id or broadcast_to):
            await self.send(json.dumps({"action": "error", "message": "Missing room ID or broadcast target."}))
            return
        
        # Sanitize message content (Prevent XSS or Injection)
        message_text = re.sub(r'[<>]', '', message_text)  # Remove HTML tags

        if not message_text and not media_list:
            await self.send(json.dumps({"action": "error", "message": "Invalid message"}))
            return


        # Check if the user is a member of the room
        is_member = await self.check_membership(room_id, user)
        if not is_member:
            await self.send(json.dumps({
                "action": "error",
                "message": "You are not a member of this chat room."
            }))
            return


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
        message, message_dict = await self.save_message(
            room_id, user, message_text, reply_to_id, reply_to_msg
        )

        # safe guarding incase no message was saved due to anything
        if message == None:
            return

        # message = await self.save_message(room_id, user, message_text, reply_to_id, reply_to_msg)
        # getting the reply message sender
        sender_username = None
        if reply_to_msg:
            sender_username = await sync_to_async(lambda: reply_to_msg.sender.username)()
        print("")
        print(message, "tobe")
        print(message.id,"idiot", message_dict)
            
        # Save media files
        saved_media = []
        if isinstance(media_list, dict):
            media_list = [media_list]

        for media_data in media_list:
            saved = await self.save_media(message, media_data)
            saved_media.append(saved)


        if room_type == "private" or room_type == "group_chat":
            # Broadcast message to the private chat room
            group_name = f"chat_{room_id}"
            await self.channel_layer.group_send(
                group_name,
                {
                    "type": "chat_message",
                    "room_id": room_id,
                    "room_type":room_type,
                    "username": user.username,
                    "user_type":user.user_type,
                    "sender": user.username,
                    "message": message_text,
                    "media": media_list,
                    "timestamp": message_dict ["timestamp"],
                    "reply_to_id": reply_to_id,
                    "reply_to_content": str(reply_to_msg),
                    "reply_message_sender":sender_username,
                    "message_id" : message_dict ['id'],
                    
                }
            )
        
        elif room_type == "broadcast":
            print("queen", f"{broadcast_to}")
            if user.is_superuser:
                timestamp_str = datetime.now().isoformat()
                await self.channel_layer.group_send(
                    f"{broadcast_to}",
                    {
                        "type": "broadcast_message",
                        "message": message_text,
                        "sender": self.user.username,
                        "media": media_list,
                        "room_type": f"{broadcast_to}",
                        "timestamp": timestamp_str,
                        "message_id" : message_dict ['id']
                    }
                )
                await self.channel_layer.group_send(
                    "global_notifications",
                    {
                        "type": "broadcast_message",
                        "message": message_text,
                        "sender": self.user.username,
                        "media": media_list,
                        "room_type": f"{broadcast_to}",
                        "timestamp": timestamp_str,
                        "message_id": message_dict['id']
                    }
                )


            
        
        print("my helper")


        # Notify all users in the chat room about missed messages
        # await self.notify_missed_messages(room_id)

        # increment unread messages in redis
        await increment_unread_count(self.user.id, room_id)
        
       

    async def broadcast_message(self, event):
        print("ygf", event)
        await self.send(json.dumps({
            "action": "broadcast_message",
            "username": event["sender"],
            "message": event["message"],
            "room_type": event["room_type"],
            "timestamp": event["timestamp"],
            "media": event.get("media", []),
            "message_id": event.get("message_id")
        }))


    async def chat_message(self, event):
        """Broadcast chat messages to room members"""
        print("")
        print("event", event)
        await self.send(json.dumps({
            "action": "message",
            "room": event.get("room_id"),
            "username": event.get("username"),
            "user_type": event.get("user_type"),
            "sender": event.get("sender"),
            "message": event.get("message"),
            "room_type":event.get("room_type"),
            'media': event.get("media"),
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



    def get_token_from_query(self, query_string):
        """Extract Bearer token from WebSocket query params"""
        query_params = dict(qc.split("=") for qc in query_string.split("&") if "=" in qc)
        token = query_params.get("Bearertoken", "").strip()
        if not token:
            print("❌ No token found in WebSocket URL")
        return token or None



    async def delete_message(self, data, user):
        message_id = data.get("message_id")
        print("deleter", message_id)
        if not message_id:
            await self.send(json.dumps({"action": "error", "message": "Message ID is required."}))
            return

        message = await database_sync_to_async(
            lambda: Message.objects.select_related("room").filter(id=message_id, sender=user).first()
        )()

        if not message:
            await self.send(json.dumps({"action": "error", "message": "Message not found or unauthorized."}))
            return

        room_id = message.room.id

        # Delete media (if any)
        deleted_media_count = await delete_message_media_and_sync_cloudinary(message)

        # If no message content or already marked, and media was deleted, fully delete
        if deleted_media_count > 0 and (not message.content.strip() or message.content == "This message has been deleted."):
            await database_sync_to_async(message.delete)()
        else:
            message.content = "This message has been deleted."
            message.deleted = True
            await database_sync_to_async(message.save)()

        # Notify the room
        await self.channel_layer.group_send(
            f"chat_{room_id}",
            {
                "type": "message_deleted",
                "message_id": message_id,
                "room_id": room_id,
                "username": user.username,
            }
        )

    async def message_deleted(self, event):
        await self.send(json.dumps({
            "action": "message_deleted",
            "message_id": event["message_id"],
            "room_id": event["room_id"],
            "username": event["username"],
        }))


    @database_sync_to_async
    def get_room_details(self, room_id):
        key = f"room_members:{room_id}"
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)

        try:
            room = ChatRoom.objects.get(id=room_id)
            members = [{"id": m.id, "username": m.username} for m in room.members.all()]
            print("room.members", room.room_type, room.creator)
            room_details = {"members":members, "room_type":room.room_type, "creator":room.creator.email}
            redis_client.setex(key, 3600, json.dumps(room_details))  # Cache for 1 hour
            return room_details
        except ChatRoom.DoesNotExist:
            return {
            "members": [],
            "room_type": None,
            "creator": None
        }


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
            decoded_token = AccessToken(token)  # Validate JWT
            user = User.objects.get(id=decoded_token["user_id"])
            return user
        except Exception as e:
            print(f"❌ JWT Authentication failed: {e}")
            return AnonymousUser()

    @database_sync_to_async
    def check_membership(self, room_id, user):
        """Check if user is a member of the room"""
        try:
            if user.is_superuser:
                return True
            else:
                room = ChatRoom.objects.get(id=room_id)
                return room.members.filter(id=user.id).exists()
        except ChatRoom.DoesNotExist:
            return False

    # @database_sync_to_async
    # def get_user_rooms_with_last_message(self, user):
    #     # """Fetch user's chat rooms along with the last message from Redis or DB"""
    #     # cache_key = f"user_rooms:{user.id}"
        
    #     # # Check Redis for cached rooms
    #     # cached_rooms = redis_client.get(cache_key)
    #     # if cached_rooms:
    #     #     print("✅ Fetching rooms from Redis cache...")
    #     #     return json.loads(cached_rooms)  # Return cached data as Python list
        
    #     # print("🔄 Fetching rooms from DB...")

    #     """Fetch user's chat rooms along with the last message"""
    #     rooms = ChatRoom.objects.filter(members=user).prefetch_related("messages")prefetch_related("messages", "members").order_by("-created_at")[offset:offset + page_size]
    #     result = []
    #     for room in rooms:
    #         last_message = room.messages.order_by("-timestamp").first()
    #         result.append({
    #             "id": room.id,
    #             "name": room.name,
    #             "last_message": last_message.content if last_message else "No messages yet",
    #             "last_message_time": last_message.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_message else "",
    #         })

    #     # Cache the result in Redis with a 10-minute expiry
    #     # redis_client.setex(cache_key, 600, json.dumps(result))  
    #     return result



    @database_sync_to_async
    def get_or_create_user_broadcast_rooms(self, user):
        """
        Get or create a broadcast chat room between different user ypes and the admin.
        """
        if not user or user.is_superuser==True:
            print("not user")
            return None


        if user:
            room_name = f"Broadcast_to_{user.user_type}"
            room, created = ChatRoom.objects.get_or_create(
                name=room_name,
                defaults={
                    "creator": user,
                    "room_type": f"broadcast_{user.user_type}"
                }
            )

            # Ensure user are members
            if created or not room.members.filter(id=user.id).exists():
                room.members.add(user)

            return {"room_id":room.id, "room_name":room.name, "room_type":room.room_type}


    # to get any available room for the admin incase a user isnt online
    @database_sync_to_async
    def get_user_broadcast_rooms_for_admin(self, user):
        """
        Get chat rooms between different user ypes and the admin.
        """
        if user.is_superuser != True:
            print("not_admin_user")
            return None


        if user:
            room = ChatRoom.objects.filter(
                room_type__in=["broadcast_HO", "broadcast_CO","broadcast_AG", "broadcast_IV"]
            ).values("id", "name", "room_type")

            print("query", room)
            results = []

            for result in room:
                print("orange",result)
                results.append({"room_id":result['id'], "room_name":result['name'], "room_type":result['room_type']})

            return results



    @database_sync_to_async
    def get_personal_user_rooms_id(self, user):
        """
        Get or create a private 1-on-1 chat room between the user and the admin.
        """
        print(user.is_superuser==True)
        if not user or user.is_superuser==True:
            print("not user")
            return None

        admin = User.objects.filter(is_superuser=True).first()
        if not admin:
            print("⚠️ No admin found. Skipping 1-on-1 room creation.")
            return None

        room_name = f"{user.email}"
        room, created = ChatRoom.objects.get_or_create(
            name=room_name,
            defaults={
                "creator": user,
                "room_type": "private"
            }
        )

        # Ensure both admin and user are members
        if created or not room.members.filter(id=user.id).exists():
            room.members.add(user, admin)

        return {"room_id":room.id, "room_name":room.name}



    
    @database_sync_to_async
    def get_user_rooms_with_last_message(self, user, page=1, page_size=10):
        """
        Fetch paginated chat rooms (group, private, broadcast) the user is in,
        along with the most recent message for each room.
        """
        offset = (page - 1) * page_size

        rooms = ChatRoom.objects.filter(members=user, room_type__in=["private", "group_chat"]).prefetch_related("messages", "members").order_by("-created_at")[offset:offset + page_size]

        result = []
        for room in rooms:
            print(room.room_type)
            last_message = room.messages.order_by("-timestamp").first()
            if not last_message and room.room_type == "private": 
                continue               
            else:
                result.append({
                    "id": room.id,
                    "name": room.name,
                    # "room_type":room.room_type,
                    "room_type": getattr(room, "room_type", "group"),
                    "last_message": last_message.content,
                    "last_message_time": last_message.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_message else "",
                })
        return result




    @database_sync_to_async
    def get_room_type_for_broadcast(self, room_id):
        room = ChatRoom.objects.filter(id=room_id).first()
        if room:
            print(room.members, room.room_type, room.creator)
            return room


    @database_sync_to_async
    def get_chat_messages(self, room_id, page):
        """Retrieve paginated chat messages"""
        PAGE_SIZE = 20
        offset = (page - 1) * PAGE_SIZE
        messages = Message.objects.filter(room_id=room_id).select_related("sender", "reply_to").prefetch_related("messagemedia").order_by("-timestamp")[offset:offset + PAGE_SIZE]

        result = []
        for msg in messages:
            media_list = [{
                "url": m.file_url,
                "type": m.media_type,
                "public_id":m.public_id
            } for m in msg.messagemedia.all()]
        
            result.append({
                "id": msg.id,
                "username": msg.sender.username,
                "user_type": msg.sender.user_type,
                "message": msg.content,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "deleted": msg.deleted,
                "reply_to": str(msg.reply_to),
                "reply_to_num": msg.reply_to_num,
                "media": media_list,
            })
        return result



    @database_sync_to_async
    def save_message(self, room_id, user, text, reply_to_num=None, reply_to_msg=None):
        """Save chat messages to the database"""
        print("oversabi", user)

        ChatRoom.objects.get_or_create
        room = ChatRoom.objects.filter(id=room_id).first()
        if not room:
            return None, None  # gracefully handle missing room

        message = Message.objects.create(
            room=room,
            sender=user,
            content=text,
            reply_to_num=reply_to_num,
            reply_to=reply_to_msg
        )

        # Exclude sender from room members for receivers
        filtered_receivers = room.members.exclude(id=user.id)
        message.receiver.add(*filtered_receivers)

        # 🧹 Invalidate Redis Cache
        redis_client.delete(f"user_rooms:{user.id}")

        return message, {
            "id": message.id,
            "message": message.content,
            "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "reply_to_id": reply_to_msg.id if reply_to_msg else None,
        }

    @sync_to_async
    def save_media(self, message_instance, media_data):
        print("incoming media:", media_data)

        # Map keys correctly
        mapped_data = {
            "file_url": media_data.get("url"),
            "public_id": media_data.get("public_id"),
            "media_type": media_data.get("type"),
        }

        serializer = MessageMediaSerializer(data=mapped_data, context={"message": message_instance})
        if serializer.is_valid(raise_exception=True):
            media = serializer.save()
            print("✅ Media saved:", media)
            return {
                "id": media.id,
                "url": media.file_url,
                "public_id": media.public_id,
                "type": media.media_type,
            }



       
    @database_sync_to_async
    def mark_messages_as_read(self, room_id, user):
        room = ChatRoom.objects.get(id=room_id)
        unread_messages = room.messages.exclude(read_by=user).only('id')

        through_model = Message.read_by.through
        new_links = [
            through_model(message_id=msg.id, user_id=user.id)
            for msg in unread_messages
        ]

        # Bulk create, ignore if already exists (you may need to handle DB constraints)
        through_model.objects.bulk_create(new_links, ignore_conflicts=True)


    # @database_sync_to_async
    # def get_each_room_type_with_last_message(self, user, room_type=None):
    #     """
    #     Fetch rooms for a user with optional room_type filtering.
    #     """
    #     query = ChatRoom.objects.filter(members=user)
    #     if room_type:
    #         query = query.filter(room_type=room_type)

    #     rooms = query.prefetch_related("messages", "members")

    #     result = []
    #     for room in rooms:
    #         last_message = room.messages.order_by("-timestamp").first()

    #         # Determine room display name
    #         if room.room_type == "private":
    #             other_member = room.members.exclude(id=user.id).first()
    #             room_name = f"Chat with {other_member.username}" if other_member else "Private Chat"
    #         elif room.room_type == "broadcast":
    #             room_name = f"Broadcast to {room.name.split('_')[-1]}"
    #         else:
    #             room_name = room.name

    #         result.append({
    #             "id": room.id,
    #             "name": room_name,
    #             "room_type": room.room_type,
    #             "last_message": last_message.content if last_message else "No messages yet",
    #             "last_message_time": last_message.timestamp.strftime("%Y-%m-%d %H:%M:%S") if last_message else "",
    #         })

    #     return result




