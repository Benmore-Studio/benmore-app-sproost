from django.urls import path
from . import views

app_name = 'property'
urlpatterns = [
    path('property-list/', views.PropertyListView.as_view(), name="property-list"),
    
    path('add-property/', views.AddProperty.as_view(), name="add-property"),
]
