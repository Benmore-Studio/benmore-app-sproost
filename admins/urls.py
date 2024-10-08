from django.urls import path
from . import views


app_name = 'admins'
urlpatterns = [
    path('dashboard/', views.AdminDashboardAPIView.as_view(), name="dashboard"),
    path('contractors/', views.ContractorsListAPIView.as_view(), name="contractors"),
    path('contractors/update/<int:pk>', views.updateContractor.as_view(), name="update_contractor"),
    path('home-owner/update/<int:pk>', views.updateHomeOwner.as_view(), name="update_home_owner"),
    path('agent/update/<int:pk>', views.UpdateAgent.as_view(), name="update_agent"),
    path('home-owners/', views.homeOwnersListView, name="homeowners"),
    path('agents/', views.agentsListView, name="agents"),
    path('active-projects/', views.activeProjectList, name="active-projects"),
    path('project-requests/', views.projectRequest, name="project-requests"),
    path('project-requests/<int:id>/', views.projectRequestDetail, name="project-requests"),
    path('change-quote-status/<int:pk>/', views.changeQuoteStatus, name="change-quote"),
]
