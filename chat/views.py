from django.shortcuts import render
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


from django.conf import settings
from django.db.models import Q

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

import cloudinary.uploader
import cloudinary.utils


from rest_framework.permissions import IsAuthenticated
from main.models import MessageMedia
from .models import Message, ChatRoom

import time
from collections import defaultdict
from chat.consumers import redis_client
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync



from django.contrib.auth import get_user_model


User = get_user_model()





class DeleteMediaView(APIView):
    """Handles media deletion from Cloudinary and local DB"""

    def delete(self, request, public_id):
        # 1. Delete from Cloudinary
        result = cloudinary.uploader.destroy(public_id)

        # 2. Delete from your DB (MessageMedia model)
        deleted_count, _ = MessageMedia.objects.filter(public_id=public_id).delete()

        return Response({
            "status": "deleted",
            "cloudinary_result": result,
            "db_deleted": deleted_count
        }, status=status.HTTP_200_OK)




@method_decorator(csrf_exempt, name='dispatch')
class CloudinarySignatureView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # Optionally retrieve extra parameters from the request if needed
        request.data.get('fileName', None)

        # Set a timestamp for the signature (usually current UNIX time)
        timestamp = int(time.time())

        # Prepare parameters to sign.
        # You can add more parameters if required by your use-case (e.g., folder, public_id).
        params_to_sign = {'timestamp': timestamp}
        # For example, if you want to include a folder:
        # params_to_sign['folder'] = 'user_uploads'

        # Generate the signature using Cloudinary's utility function.
        # Make sure your CLOUDINARY_API_SECRET is configured in settings.
        signature = cloudinary.utils.api_sign_request(
            params_to_sign,
            settings.CLOUDINARY_STORAGE["API_SECRET"]
        )

        # Prepare response data
        data = {
            'signature': signature,
            'timestamp': timestamp,
            'api_key': settings.CLOUDINARY_STORAGE["API_KEY"],
            'cloud_name': settings.CLOUDINARY_STORAGE["CLOUD_NAME"]
        }
        return Response(data, status=status.HTTP_200_OK)





class CreateRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        room_name = request.data.get('roomName')
        member_ids = request.data.get('members', [])

        if not room_name:
            return Response({'error': 'Room name is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optional: ensure uniqueness of room name
        if ChatRoom.objects.filter(name=room_name).exists():
            return Response({'error': 'A room with this name already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        # Create the room with the requesting user as creator
        chat_room = ChatRoom.objects.create(name=room_name, creator=request.user)
        
        # Add the creator to the room by default)
        chat_room.members.add(request.user)

        # Add each selected user
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                chat_room.members.add(user)
            except User.DoesNotExist:
                # Optionally handle this case if user doesn't exist
                pass
        
        print("ogo")
        # Send WebSocket Notification to Connected Users**
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "global_notifications",  # Broadcast to all connected users
            {
                "type": "notify_new_room",
                "room": {
                    "id": chat_room.id,
                    "name": chat_room.name
                }
            }
        )
        print(chat_room.id, "✅ WebSocket event successfully sent!", chat_room.name)
        
        return Response({
            'success': True,
            'roomId': chat_room.id,
            'roomName': chat_room.name
        }, status=status.HTTP_201_CREATED)



class AddMembersAPIView(APIView):
    """ Allow only the room creator to add members to an existing chat room """
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Get the chat room
        chat_room = get_object_or_404(ChatRoom, id=room_id)

        # Ensure that only the room creator (admin) can add new members
        if chat_room.creator != request.user:
            return Response({'error': 'Only the room creator can add members.'}, status=status.HTTP_403_FORBIDDEN)

        # Get user IDs from request
        member_ids = request.data.get('members', [])

        if not member_ids:
            return Response({'error': 'No members provided to add.'}, status=status.HTTP_400_BAD_REQUEST)

        added_users = []
        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                if user not in chat_room.members.all():  # Prevent duplicates
                    chat_room.members.add(user)
                    added_users.append(user.username)
            except User.DoesNotExist:
                continue  # Ignore invalid user IDs
        # nvalidate Redis cache for room members
        redis_client.delete(f"room_members:{room_id}")


        return Response({
            'success': True,
            'message': 'Users added successfully.',
            'added_users': added_users
        }, status=status.HTTP_200_OK)



class LeaveRoomAPIView(APIView):
    """ Allow a user to leave a chat room """
    permission_classes = [IsAuthenticated]

    def post(self, request, room_id):
        # Get the chat room
        chat_room = get_object_or_404(ChatRoom, id=room_id)

        # Ensure the user is in the chat room
        if request.user not in chat_room.members.all():
            return Response({'error': 'You are not a member of this chat room.'}, status=status.HTTP_400_BAD_REQUEST)

        # Remove the user from the room
        chat_room.members.remove(request.user)

        return Response({
            'success': True,
            'message': 'You have left the chat room.'
        }, status=status.HTTP_200_OK)



class DeleteRoomAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, room_id):
        # Fetch the chat room or return 404 if it does not exist
        room = get_object_or_404(ChatRoom, id=room_id)

        if not (request.user.is_superuser or request.user == room.creator):
            return Response({"detail": "You do not have permission to delete this room."},
                            status=status.HTTP_403_FORBIDDEN)

        room.delete()

         # Send WebSocket Notification to Connected Users**
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "global_notifications",  # Broadcast to all connected users
            {
                "type": "notify_delete_room",
                "room": {
                    "message": "room deleted",
                }
            }
        )
        return Response(
            {"detail": "Chat room deleted successfully.", "success": True},
            status=status.HTTP_200_OK
        )


# chatroom search message view
class SearchMessagesView(APIView):
    """
    API endpoint to search messages in chat rooms.
    Users can search globally or within a specific chat room.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        room_id = request.GET.get('room_id')  # Optional: filter messages by room

        if not query:
            return Response({"error": "Query is required"}, status=400)

        messages = Message.objects.filter(Q(content__icontains=query))

        if room_id:
            messages = messages.filter(room_id=room_id)

        # Group messages by room
        grouped_results = defaultdict(list)

        for msg in messages:
            grouped_results[msg.room.id].append({
                "id": msg.id,
                "room_id": msg.room.id,
                "room_name": msg.room.name,
                "content": msg.content,
                "sender": msg.sender.username,
                "timestamp": msg.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })

        # Convert defaultdict to a normal dict before returning
        results = [{"room_id": room_id, "room_name": messages[0]["room_name"], "messages": messages} 
                   for room_id, messages in grouped_results.items()]

        return Response({"results": results})


class AdminSearchUserAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '')
        if query:
            users = User.objects.filter(
                Q(username__icontains=query) | Q(email__icontains=query)
            )
            results = [
                {'id': user.id, 'username': user.username, 'email': user.email}
                for user in users
            ]
            return Response({'users': results})
        return Response({'users': []})







# ok, first you need to convert to drf class based views-from django.http import JsonResponse
# import cloudinary.uploader

# def delete_media(request, public_id):
#     """Delete media from Cloudinary"""
#     result = cloudinary.uploader.destroy(public_id)
#     return JsonResponse({"status": "deleted", "result": result}) , secondly you ddnt give me the html struture with is description of where to plu this functions, lastly you added message to my media model? whats that field for and why?-class Media(models.Model):
#     message = models.ForeignKey(Message, related_name="media", on_delete=models.CASCADE)
#     url = models.URLField()
#     public_id = models.CharField(max_length=255)  # Cloudinary ID for deletion
#     media_type = models.CharField(max_length=10, choices=[("image", "Image"), ("video", 
