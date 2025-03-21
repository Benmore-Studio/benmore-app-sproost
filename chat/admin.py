from django.contrib import admin
from .models import ChatRoom, ChatRoomInvitation, Message, RoomMembership


# Register your models here.

admin.site.register(ChatRoom)
admin.site.register(ChatRoomInvitation)
admin.site.register(Message)
admin.site.register(RoomMembership)
