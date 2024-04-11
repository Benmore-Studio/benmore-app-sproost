from django.urls import path
from . import views 


app_name = 'profile'
urlpatterns = [
    path('', views.contractor_profile_view, name='contractor_profile'),
    path('edit-profile/<int:pk>', views.EditProfileView.as_view(), name="edit-profile"),
    path('search-view/', views.search_view, name="search-view"),
    path('search-view-results/', views.search_view_results, name="search-view-results"),
    path('edit-profile-request/', views.editProfileRequest, name="edit-profile-request"),
    
    path('upload-image/', views.upload_image, name='upload-image')
]