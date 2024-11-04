from django.urls import path
from . import views 


app_name = 'profile'
urlpatterns = [
    # path('', views.ContractorProfileAPIView.as_view(), name=""),
    path('edit-users-profile/', views.EditUsersProfileAPIView.as_view(), name="edit-users-profile"),
    # path('agent/update/', views.EditAgentProfileAPIView.as_view(), name="edit-agent-profile"),
    # path('contractor/update/', views.ContractorProfileEditAPIView.as_view(), name="edit-contractor-profile"),
    path('search-view/', views.ContractorSearchAPIView.as_view(), name="search_contractor"),
    path('change-dp-request/', views.ChangeProfilePictureAPIView.as_view(), name="change-dp-request"),
    path('upload/', views.UploadApiView.as_view(), name='upload'),
    # path('search-view-results/', views.search_view_results, name="search-view-results"),
    # path('show-agent-menu/', views.show_agent_menu_view, name="show-agent-menu"),
    # path('show-agent-message/', views.show_agent_message_view, name="show-agent-message"),
    # path('update_onboarding_status/', views.update_onboarding_status, name="update_onboarding_status"),
]