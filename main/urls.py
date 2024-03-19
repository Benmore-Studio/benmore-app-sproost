from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

app_name = 'main'
urlpatterns = [
    path('', views.home, name="home"),
    path('menu/', views.MenuList, name="menu"),
    path('request-quotes/', views.requestQuotes, name="request-quotes"),
    path('quotes-summary/', views.QuotationReturn, name="quotes-summary"),
    path('assign-agent/', views.assignAgent, name="assign-agent"),
    path('property-list/', views.propertyList, name="property-list"),
    path('add-property/', views.addProperty, name="add-property"),
    path('edit-profile/', views.editProfile, name="edit-profile"),
    path('contractors/', views.contractors, name="contractors"),
    path('contractors/<str:profession>/', views.contractorDetail, name="contractors"),
    path('login/', views.loginUser, name="login"),
    path('signup/', views.signUpUser, name="signup"),
    # admin
    path('login-admin/', views.loginAdmin, name="login-admin"),
    path('dashboard/', views.adminDashboard, name="dashboard"),
    path('project-requests/', views.projectRequest, name="project-requests"),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)