from django.urls import path
from .views import PropertyCreateView,PropertyRetrieveView, PropertyUpdateView, UserPropertyListView, PropertyDeleteView, PropertyListAPIView


app_name = 'property'

urlpatterns = [
    path('create', PropertyCreateView.as_view(), name="properties"),
    path('<int:pk>', PropertyRetrieveView.as_view(), name="properties"),
    path('<int:pk>/update', PropertyUpdateView.as_view(), name="properties"),
    path('<int:pk>/delete', PropertyDeleteView.as_view(), name="property-delete"),
    path('me/all', UserPropertyListView.as_view(), name="contractor-all-properties"),
    path('all', PropertyListAPIView.as_view(), name="contractor-all-properties"),
 ]

 