from django.urls import path
from . import views


app_name = 'admins'
urlpatterns = [
    path('project-requests/', views.projectRequest, name="project-requests"),
    path('project-requests/<int:id>/', views.projectRequestDetail, name="project-requests"),
]

