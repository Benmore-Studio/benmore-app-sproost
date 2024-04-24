from django.urls import path
from . import views


app_name = 'admins'
urlpatterns = [
    path('dashboard/', views.adminDashboard, name="dashboard"),
    path('contractors/', views.contractorsListView, name="contractors"),
    path('home-owners/', views.homeOwnersListView, name="homeowners"),
    path('agents/', views.agentsListView, name="agents"),
]
