from django.urls import path, include

from . import views 





urlpatterns = [

    path('cloudinary-signature/', views.CloudinarySignatureView.as_view(), name='cloudinary-signature'),
    path('delete_media/<str:public_id>/', views.DeleteMediaView.as_view(), name='delete_media'),
    path('live_admin_user_search/', views.AdminSearchUserAPIView.as_view(), name="live_admin_user_search"),
    path('chat/create_room/', views.CreateRoomAPIView.as_view(), name='create_room'),
    path("search_messages/", views.SearchMessagesView.as_view(), name="search_messages"),
    path('rooms/<int:room_id>/add-members/', views.AddMembersAPIView.as_view(), name='add-members'),
    path('rooms/<int:room_id>/leave/', views.LeaveRoomAPIView.as_view(), name='leave-room'),
    path('rooms/<int:room_id>/delete/', views.DeleteRoomAPIView.as_view(), name='delete-room'),

]
