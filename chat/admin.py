from django.contrib import admin
from .models import ChatRoom, ChatRoomInvitation


# Register your models here.

admin.site.register(ChatRoom)
admin.site.register(ChatRoomInvitation)
