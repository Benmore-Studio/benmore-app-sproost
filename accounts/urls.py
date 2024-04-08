from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.loginUser, name="login"),
    path('signup/', views.signUpUser, name="signup"),
]

