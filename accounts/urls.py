from django.urls import path, include

from .views import (CustomLoginView, 
                    validate_phone_numbers, 
                    logout_user, 
                    ManualSignupView,
                    GoogleSignUp,
                    MyTokenObtainPairView,
                    # CustomSignupView, 
                    select_user_type,
                    verify_email,
                    verify_email_two,
                    final_email_verification
                    )
from django.contrib.auth.views import LogoutView

urlpatterns = [

    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    # path('login/', CustomLoginView.as_view(), name='account_login'),
    path('google-signup/', GoogleSignUp.as_view(), name='google_signup'),
    path('account/signup/', ManualSignupView.as_view(), name='account_signup'),
    path('verify_email/', verify_email, name='verify_email'),
    path('verify_email_two/', verify_email_two, name='verify_email_two'),
    path('final_email_verification/', final_email_verification, name='final_email_verification'),
    path('validate-phone', validate_phone_numbers , name='validate_number'),
    path('logout', logout_user, name='logout'),
    path('select_user_type', select_user_type, name='select_user_type'),
    # path('referral/', referral_dashboard, name='referral_dashboard'),

    # other urls...
]