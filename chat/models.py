from django.db import models
from accounts.models import User


# Create your models here.

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


class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name="messages", on_delete=models.CASCADE)
    content = models.TextField(max_length=512)
    sender= models.ForeignKey(User, on_delete=models.CASCADE, related_name="messagesender")
    receiver= models.ManyToManyField(User, blank=True, related_name="messagereceiver")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.content}: {self.content[:20]}..."  # Show a preview of the message'

