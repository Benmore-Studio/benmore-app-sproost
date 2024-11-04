from django.urls import path
from .views import DashboardView

app_name = "admin"

urlpatterns = [
    # path("dashboard/", DashboardView.as_view(), name="admin-dashboard"),
    path("dashboard/", DashboardView, name="admin-dashboard"),
   
]
