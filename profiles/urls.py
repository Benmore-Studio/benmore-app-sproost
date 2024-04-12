from django.urls import path
from . import views 


app_name = 'profile'
urlpatterns = [
    path('', views.contractor_profile_view, name='contractor_profile'),
    path('contractor-details/<int:pk>/', views.contractorDetails.as_view(), name='contractor_details'),
    # path('edit-profile/<int:pk>', views.EditProfileView.as_view(), name="edit-profile"),
    path('edit-profile/', views.editProfile, name="edit-profile"),
    path('search-view/', views.search_view, name="search_contractor"),
    # path('edit-profile/<int:pk>', views.EditProfileView.as_view(), name="edit-profile"),
    path('search-view-results/', views.search_view_results, name="search-view-results"),
    path('edit-profile-request/', views.ContractorProfileEditView, name="edit-profile-request"),
    path('edit-homeowners-profile-request/', views.editHomeOwnerProfileRequest, name="edit-homeowners-profile-request"),
]