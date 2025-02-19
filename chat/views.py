import uuid
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatRoomInvitation
from rest_framework.views import APIView


User = get_user_model()


class AddChatMemberView(APIView):
    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        # Only the room creator can add members
        if request.user != room.creator:
            return HttpResponseForbidden("Only the room creator can add members.")

        user_identifier = request.POST.get('user_identifier')
        if not user_identifier:
            return JsonResponse({"error": "User identifier missing."}, status=400)

        try:
            # First try to get by username, then by email
            user = User.objects.get(username=user_identifier)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=user_identifier)
            except User.DoesNotExist:
                # No matching user; create an invitation.
                token = uuid.uuid4().hex
                invite_url = request.build_absolute_uri(
                    reverse('chat_invite', kwargs={'token': token})
                )
                ChatRoomInvitation.objects.create(
                    room=room,
                    email=user_identifier,
                    token=token
                )
                send_mail(
                    subject="You're invited to join a chat room",
                    message=f"Click the link to join the chat room '{room.name}': {invite_url}",
                    from_email="noreply@example.com",
                    recipient_list=[user_identifier],
                )
                return JsonResponse({"status": "Invitation sent"}, status=200)

        # If the user was found, add them to the room
        room.members.add(user)
        return JsonResponse({"status": "User added to the room"}, status=200)



class JoinInvitedRoomView(APIView):
    def get(self, request, token):
        # Look up an invitation that is not yet used.
        invitation = get_object_or_404(ChatRoomInvitation, token=token, used=False)
        room = invitation.room
        room.members.add(request.user)

        # Invalidate the invitation
        invitation.used = True
        invitation.save()

        # Prepare the redirect URL
        redirect_url = f'/chat/room/{room.name}/'
        
        # Return JSON with the redirect URL so the Flutter client can handle it
        return Response({"redirect_url": redirect_url}, status=status.HTTP_200_OK)
    
# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class AddUserSearchAPIView(APIView):
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



