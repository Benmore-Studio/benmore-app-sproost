from django.urls import path
from . import views

app_name = 'property'
urlpatterns = [
    path('dashboard/<int:pk>', views.agents_home_owner_account, name="agent-homeowner-dashboard"),
    path('all-property', views.view_all_property, name="all-property"),
]
