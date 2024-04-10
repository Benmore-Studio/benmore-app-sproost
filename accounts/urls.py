from django.urls import path, include
from .views import CustomLoginView, validate_phone_numbers

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('validate-phone', validate_phone_numbers , name='validate_number'),
    # other urls...
]