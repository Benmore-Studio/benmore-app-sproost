from django.contrib import admin
from django.urls import path
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls', namespace='main')),
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    path('profiles/', include('profiles.urls', namespace='profile')),
    path('quotes/', include('quotes.urls', namespace='quotes')),
    # path('admin/', include('admins.urls', namespace='admins')),
    
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)