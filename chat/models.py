from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    creator = models.ForeignKey(User, related_name='created_rooms', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class ChatRoomInvitation(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='invitations', on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f"Invitation for {self.email} to {self.room.name}"

