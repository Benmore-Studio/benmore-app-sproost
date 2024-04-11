from django.urls import path, include
from .views import CustomLoginView, validate_phone_numbers, logout
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('validate-phone', validate_phone_numbers , name='validate_number'),
    path('logout', logout, name='logout'),
    # other urls...
]