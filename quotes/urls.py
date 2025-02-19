from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PropertyAPIView, QuotesAPIView, PropertySearchView, ViewIndividualQuote

app_name = 'quotes'

# router = DefaultRouter()
# router.register(r'projects', ProjectViewSet)

urlpatterns = [
    path('request-quotes/', QuotesAPIView.as_view(), name="request-quotes"),
    path('properties/', PropertyAPIView.as_view(), name="properties"),
    path('search-properties/', PropertySearchView.as_view(), name="search-properties"),
    path('view_individual_quote/<int:property_id>/', ViewIndividualQuote.as_view(), name="view_individual_quote"),
    # path('request-quotes/<str:name>', Quotes.as_view(), name="request-quotes"),
    # path('api/', include(router.urls)),
]
