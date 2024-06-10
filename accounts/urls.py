from django.urls import path, include

from .views import CustomLoginView, validate_phone_numbers, logout_user, CustomSignupView
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='account_login'),
    path('signup/', CustomSignupView.as_view(), name='account_signup'),
    path('validate-phone', validate_phone_numbers , name='validate_number'),
    path('logout', logout_user, name='logout'),
    # path('referral/', referral_dashboard, name='referral_dashboard'),

    # other urls...
]