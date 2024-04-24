from django.urls import path
from . import views


app_name = 'admins'
urlpatterns = [
    path('dashboard/', views.adminDashboard, name="dashboard"),
    path('contractors/', views.contractorsListView, name="contractors"),
    path('home-owners/', views.homeOwnersListView, name="homeowners"),
    path('agents/', views.agentsListView, name="agents"),
    path('active-projects/', views.activeProjectList, name="active-projects"),
    path('project-requests/', views.projectRequest, name="project-requests"),
    path('project-requests/<int:id>/', views.projectRequestDetail, name="project-requests"),
]
