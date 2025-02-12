from django.urls import path, include

from .views import ( 
                    ManualSignupView,
                    GoogleTokenAuthenticateView,
                    CompleteSignupView,
                    MyTokenObtainPairView,
                    SendOTPView,
                    VerifyOTPView,
                    ChangePasswordView,CustomLogoutView,
                    )
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.decorators.csrf import csrf_exempt



urlpatterns = [

    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('google-signup/', GoogleTokenAuthenticateView.as_view(), name='google_signup'),
    path('complete-google-signup/', CompleteSignupView.as_view(), name='complete_google_signup'),
    path('manual_signup/', ManualSignupView.as_view(), name='manual_signup'),
    # path('validate-phone', validate_phone_numbers , name='validate_number'),
    path('logout/', csrf_exempt(CustomLogoutView.as_view()), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('send-otp/<str:otp_type>/', SendOTPView.as_view(), name='send_otp'),
    # path('send-otp-password/<str:otp_type>/', SendOTPView.as_view(), name='send_otp_password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    # path('referral/', referral_dashboard, name='referral_dashboard'),

    # other urls...
]