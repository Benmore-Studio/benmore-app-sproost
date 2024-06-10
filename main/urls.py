from django.urls import path
from . import views


app_name = 'main'
urlpatterns = [
    path('', views.home, name="home"),
    path('menu/', views.MenuList, name="menu"),
    path('quotes-summary/', views.QuotationReturn, name="quotes-summary"),
    path('assign-agent/', views.AssignAgentView.as_view(), name="assign-agent"),
    path('contractors/', views.contractors, name="contractors"),
    path('contractors/<str:profession>/', views.contractorDetail, name="contractors"),
    path('assigned-projects/', views.Assigned_projects, name="assigned-projects"),
]

