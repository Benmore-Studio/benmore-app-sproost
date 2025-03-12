from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import QuotesAPIView,ListQuotesForPropertyView

app_name = 'quotes'

# router = DefaultRouter()
# router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('request-quotes/', QuotesAPIView.as_view(), name="request-quotes"),
    path('view_individual_quote/<int:property_id>/', ListQuotesForPropertyView.as_view(), name="view_individual_quote"),
    # path('request-quotes/<str:name>', Quotes.as_view(), name="request-quotes"),
    # path('api/', include(router.urls)),


]
