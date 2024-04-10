from django.urls import path
from . import views 


app_name = 'profile'
urlpatterns = [
    path('', views.contractor_profile_view, name='contractor_profile')
]