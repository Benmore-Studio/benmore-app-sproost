from django.urls import path
from . import views


app_name = 'main'
urlpatterns = [
    path('', views.HomeView.as_view(), name="home"),
    path('home-owners/<str:name>/', views.HomeOwnerWithSlugNameView.as_view(), name="home_owner_with_slug_name"),
    path('assign-agent/', views.AssignAgentAPIView.as_view(), name="assign-agent"),
    path('contractors/<str:profession>/', views.contractorDetail, name="contractors"),
    path('assigned-projects/', views.AssignedProjectsView.as_view(), name="assigned-projects"),
    # path('menu/', views.MenuList, name="menu"),
    # path('quotes-summary/', views.QuotationReturn, name="quotes-summary"),
    # path('contractors/', views.contractors, name="contractors"),
]

