from django.urls import path
from . import views 


app_name = 'profile'
urlpatterns = [
    # path('', views.ContractorProfileAPIView.as_view(), name=""),
    path('edit-users-profile/', views.EditUsersProfileAPIView.as_view(), name="edit-users-profile"),
    path('contractor-change-dp-request/', views.ChangeProfilePictureAPIView.as_view(), name="change-dp-request"),
    path('contractor-upload/', views.ContractorUploadApiView.as_view(), name='upload'),
    path('all-agents/', views.AllAgents.as_view(), name="all-agents"),
    path('invite-agents/', views.InviteAgentView.as_view(), name="invite-agents"),
    path('list-contractors/', views.ContractorListAPIView.as_view(), name="list-contractors"),
    path('get-clients-agents-or-contractors/<str:query_type>/', views.GetUserClientsOrAgents.as_view(), name="get-clients-or-agents"),
    path('user-listing-or-properties/', views.GetUserListingsOrProperties.as_view(), name="user-listing-or-properties"),

    # path('agent/update/', views.EditAgentProfileAPIView.as_view(), name="edit-agent-profile"),
    # path('contractor/update/', views.ContractorProfileEditAPIView.as_view(), name="edit-contractor-profile"),
    # path('search-view/', views.ContractorSearchAPIView.as_view(), name="search_contractor"),
    # path('search-view-results/', views.search_view_results, name="search-view-results"),
    # path('show-agent-message/', views.show_agent_message_view, name="show-agent-message"),
    # path('update_onboarding_status/', views.update_onboarding_status, name="update_onboarding_status"),
]