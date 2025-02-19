# urls.py
from django.urls import path
from .views import AddChatMemberView, JoinInvitedRoomView, AddUserSearchAPIView

urlpatterns = [
    path('chat/add_member/<int:room_id>/', AddChatMemberView.as_view(), name='add_chat_member'),
    path('chat/invite/<str:token>/', JoinInvitedRoomView.as_view(), name='chat_invite'),
    path('api/user-search/', AddUserSearchAPIView.as_view(), name='user_search'),
]
