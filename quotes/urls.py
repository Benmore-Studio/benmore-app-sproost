from django.urls import path, include
from .views import QuotesAPIView

from rest_framework.routers import DefaultRouter
from .views import ProjectViewSet

app_name = 'quotes'

router = DefaultRouter()
router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('request-quotes/', QuotesAPIView.as_view(), name="request-quotes"),
    # path('request-quotes/<str:name>', Quotes.as_view(), name="request-quotes"),
    path('api/', include(router.urls)),
]