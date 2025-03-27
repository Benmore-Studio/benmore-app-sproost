from django.db import models
from accounts.models import User
from django.contrib.contenttypes.fields import GenericRelation



# Create your models here.

ROOM_TYPE_CHOICES = (
        ("private", "Private"),  
        ("group", "Group"),      
    )

class ChatRoom(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    creator = models.ForeignKey(User, related_name='created_rooms', on_delete=models.CASCADE)
    members = models.ManyToManyField(User, through='RoomMembership', related_name="chat_rooms")
    created_at = models.DateTimeField(auto_now_add=True)
    room_type = models.CharField(
        max_length=20,
        choices=(("group", "Group"), ("private", "Private"), ("broadcast", "Broadcast")),
        default="private"
    )

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
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    read_by = models.ManyToManyField(User, blank=True, related_name="messages_read", help_text=" Track who has read it")  # Track who has read it
    reply_to_num = models.IntegerField(blank=True, null=True)
    reply_to = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )
    deleted = models.BooleanField(default=False)
    media_paths = GenericRelation("main.Media")  


    def __str__(self):
        return f'{self.content}: {self.content[:20]}'


class RoomMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'room')


