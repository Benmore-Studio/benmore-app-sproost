from django.urls import path, include

from .views import ( 
                    ManualSignupView,
                    GoogleSignUp,
                    MyTokenObtainPairView,
                    )
from django.contrib.auth.views import LogoutView
from rest_framework_simplejwt.views import TokenRefreshView
from django.views.decorators.csrf import csrf_exempt



urlpatterns = [

    path('login/', MyTokenObtainPairView.as_view(), name='login'),
    path('google-signup/', GoogleSignUp.as_view(), name='google_signup'),
    path('account/manual_signup/', ManualSignupView.as_view(), name='manual_signup'),
    # path('validate-phone', validate_phone_numbers , name='validate_number'),
    path('logout/', csrf_exempt(LogoutView.as_view()), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('referral/', referral_dashboard, name='referral_dashboard'),

    # other urls...
]