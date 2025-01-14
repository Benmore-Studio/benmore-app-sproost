from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet, PropertyAPIView, QuotesAPIView

app_name = 'quotes'

# router = DefaultRouter()
# router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('request-quotes/', QuotesAPIView.as_view(), name="request-quotes"),
    path('properties/', PropertyAPIView.as_view(), name="properties"),
    # path('request-quotes/<str:name>', Quotes.as_view(), name="request-quotes"),
    # path('api/', include(router.urls)),
]
