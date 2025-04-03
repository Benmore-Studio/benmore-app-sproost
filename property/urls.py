from django.urls import path
from .views import (PropertyCreateView,PropertyRetrieveView, PropertyUpdateView, UserPropertyListView, 
PropertyDeleteView, PropertyListAPIView, ClientListView, PropertyListForClientView)


app_name = 'property'

urlpatterns = [
    path('create', PropertyCreateView.as_view(), name="properties"),
    path('<int:pk>', PropertyRetrieveView.as_view(), name="properties"),
    path('<int:pk>/update', PropertyUpdateView.as_view(), name="properties"),
    path('<int:pk>/delete', PropertyDeleteView.as_view(), name="property-delete"),
    path('me/all', UserPropertyListView.as_view(), name="contractor-all-properties"),
    path('all', PropertyListAPIView.as_view(), name="contractor-all-properties"),
    path('agents/me/clients', ClientListView.as_view(), name='agents-clients'),
    path('clients/<int:client_id>/properties', PropertyListForClientView.as_view(), name='agents-clients')
 ]

 