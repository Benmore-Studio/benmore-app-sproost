from django.urls import path
from .views import Quotes

app_name = 'quotes'

urlpatterns = [
    path('request-quotes/', Quotes.as_view(), name="request-quotes"),
]