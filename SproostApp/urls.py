from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf.urls import handler400, handler500, handler404
from django.conf.urls.static import static
from django.conf import settings



from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView, LogoutView, UserDetailsView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django.urls import path

# handler400 = 'accounts.views.custom_bad_request'
# handler404 = 'accounts.views.custom_bad_request'
# handler500 = 'accounts.views.custom_server_error'

urlpatterns = [

    # path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # path('dj-rest-auth/social/', include('dj_rest_auth.social.urls')),  

    path('admin/', admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs"),
    path('api/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/auth/', include('dj_rest_auth.urls')),
    # path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    # path("register/", RegisterView.as_view(), name="rest_register"),
    # path("login/", LoginView.as_view(), name="rest_login"),
    # path("logout/", LogoutView.as_view(), name="rest_logout"),
    # path("user/", UserDetailsView.as_view(), name="rest_user_details"),

    # path('admin/', admin.site.urls),
    path('user-admin/', include('admins.urls', namespace='admins')),
    path('', include('main.urls', namespace='main')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls', namespace='profile')),
    path('quotes/', include('quotes.urls', namespace='quotes')),
    path('property/', include('property.urls', namespace='property')),
]




if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
