from django.urls import path
from . import views

app_name = 'property'
urlpatterns = [
    path('dashboard/<int:pk>', views.AgentsHomeOwnerAccountAPIView.as_view(), name="agent-homeowner-dashboard"),
    # path('all-property', views.view_all_property, name="all-property"),
]
