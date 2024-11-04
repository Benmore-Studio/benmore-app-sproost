from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf.urls import handler400, handler500, handler404
from django.conf.urls.static import static
from django.conf import settings

# handler400 = 'accounts.views.custom_bad_request'
# handler404 = 'accounts.views.custom_bad_request'
# handler500 = 'accounts.views.custom_server_error'

urlpatterns = [
    path('admin/', admin.site.urls),
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
