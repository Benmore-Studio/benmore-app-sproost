from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'
urlpatterns = [
    path('', views.home, name="home"),
    path('request-quotes/', views.requestQuotes, name="request-quotes"),
    path('quotes-summary/', views.QuotationReturn, name="quotes-summary"),
    path('assign-agent/', views.assignAgent, name="assign-agent"),
    path('property-list/', views.propertyList, name="property-list"),
    path('login/', views.loginUser, name="login"),
    path('signup/', views.signUpUser, name="signup"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)