from django.urls import path
from . import views


app_name = 'admins'
urlpatterns = [
    path('dashboard/', views.AdminDashboardAPIView.as_view(), name="dashboard"),
    path('contractors/', views.ContractorsListAPIView.as_view(), name="contractors"),
    path('home-owners/', views.HomeOwnersListAPIView.as_view(), name="homeowners"),
    path('agents/', views.AgentsListAPIView.as_view(), name="agents"),
    path('project-requests/', views.ProjectRequestListAPIView.as_view(), name="project-requests"),
    path('project-requests/<int:id>/', views.ProjectRequestDetailAPIView.as_view(), name="project-requests"),
    path('active-projects/', views.ActiveProjectListAPIView.as_view(), name="active-projects"),
    # path('change-quote-status/<int:pk>/', views.ChangeQuoteStatusAPIView.as_view(), name="change-quote"),
    path('contractors/update/<int:pk>/', views.UpdateContractorAPIView.as_view(), name="update-contractor"),
    path('home-owner/update/<int:pk>/', views.UpdateHomeOwnerAPIView.as_view(), name="update-home_owner"),
    path('agent/update/<int:pk>/', views.UpdateAgentAPIView.as_view(), name="update-agent"),
  
]
