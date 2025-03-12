 
from accounts.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from quotes.services import QuoteService
from django.contrib.auth import get_user_model
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView, RetrieveAPIView 
from rest_framework.permissions import IsAuthenticated
from profiles.serializers import PropertySerializer
from property.models import Property
from property.serializers import PropertyRetrieveSerializer
from .models import QuoteRequest, QuoteRequestStatus, UserPoints
from .serializers import   QuoteRequestSerializer
from main.serializers import BulkMediaSerializer
from django.db.models import Prefetch
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
import json
from django.core.exceptions import ValidationError



User = get_user_model()


class QuotesAPIView(GenericAPIView):
    """
    API View to handle quote requests and file uploads.

    ----------------------------
    INPUT PARAMETERS:
    - GET: Fetch initial form data for quote requests based on user type.
    - POST: Submit quote request data, including media files (if any).

    -----------------------------
    OUTPUT PARAMETERS:
    - GET: Returns initial data for the quote request.
    - POST: Returns success or error messages upon submission.
    """
    serializer_class = QuoteRequestSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated] 

    def get_user(self, user):
        return User.objects.prefetch_related('quote_requests').get(id=user.id)

    def get_initial_data(self, user):
        """
        Get initial data for the form based on the user type (HO or AG).
        """
        home_owner_quotes = self.get_user(user)
        quotes_data = QuoteRequestSerializer(home_owner_quotes.quote_requests.all(), many=True).data
        if user.user_type == 'HO':
            return {
                'contact_phone': str(user.phone_number),
                'custom_home_owner_id': user.pk,
                'created_by_agent': user.pk,
                "quotes": quotes_data
            }
        elif user.user_type == 'AG':
            return {
                'contact_phone': str(user.phone_number),
            }
        return {}


    def handle_no_permission(self):
        """
        Custom response for unauthenticated requests.
        """
        return Response({'error': 'You are not authenticated. Please log in and try again.'}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, **_):
        """
        Handle GET request to return initial form data.
        """
        user = request.user
        if not user.is_authenticated: 
            return self.handle_no_permission()
        if request.user.user_type == 'AG' or request.user.user_type == 'HO':
            initial_data = self.get_initial_data(user)
            return Response(initial_data, status=status.HTTP_200_OK)
        else:
            return Response({"errors":"User type has no quotes"}, status=status.HTTP_400_BAD_REQUEST)
 

    @extend_schema(
        summary="Submit a Quote Request",
        description="""
        Allows **Home Owners (`HO`)** and **Agents (`AG`)** to submit a quote request.

        **Required Fields:**
        - `title` (String) - Title of the quote request.
        - `summary` (String) - Description of the quote request.
        - `property` (Integer) - ID of the associated property.
        - `quote_type` (String) - Type of quote request.
        - `contact_phone` (String) - Contact phone number.

        **Optional Fields:**
        - `media` (File Upload - Multiple Files Allowed) - Images, videos, or document files.

        **Restrictions:**
        - Only **Home Owners (`HO`)** and **Agents (`AG`)** can create quotes.
        """,
        parameters=[
            OpenApiParameter(name="title", type=OpenApiTypes.STR, required=True, description="Title of the quote request."),
            OpenApiParameter(name="summary", type=OpenApiTypes.STR, required=True, description="Summary of the quote request."),
            OpenApiParameter(name="property", type=OpenApiTypes.INT, required=True, description="ID of the associated property."),
            OpenApiParameter(name="quote_type", type=OpenApiTypes.STR, required=True, description="Type of quote request."),
            OpenApiParameter(name="contact_phone", type=OpenApiTypes.STR, required=True, description="Contact phone number."),
            OpenApiParameter(name="media", type=OpenApiTypes.STR, required=False, description="Multiple media files (images, videos, documents)."),
        ],
        responses={201: OpenApiTypes.OBJECT, 400: OpenApiTypes.OBJECT},
    )

    def post(self, request, **_):
        """
        Handle POST request to submit quote request data, including media files.
        """
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Check if user is allowed to create quotes
        if request.user.user_type not in ['AG', 'HO']:
            return Response({"error": "User type not allowed to create quotes"}, status=status.HTTP_400_BAD_REQUEST)

        # Prepare data for validation
        data_copy = request.data.copy()
        data_copy['user'] = user.id
        
        # Validate the data using serializer
        serializer = self.get_serializer(data=data_copy)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        # Prepare form data for the service
        form_data = serializer.validated_data
        form_data['user'] = user
        
        # Handle media file uploads
        form_data['media'] = None
        if 'media' in request.FILES:
            form_data['media'] = request.FILES.getlist('media')
        
        # Get user profile and use QuoteService to create the quote
        user_profile = self.get_user(user)
        quote_service = QuoteService(request, user_profile)
        
        # Create the quote using the service
        result, created_quote = quote_service.create(form_data, user_profile, model_passed=QuoteRequest)
        
        if result:
            # Update the property to indicate it has quotes
            try:
                user_property = Property.objects.get(id=data_copy['property'])
                user_property.has_quotes = True
                user_property.save()
                
                if (
                        result.status == QuoteRequestStatus.accepted
                        and result.user
                        and result.user.user_type == 'AG'
                    ):
                    print(f'Quote request {result.id} passed validation for points award')
                    # Award points regardless of whether it's admin or API request
                    accepted_count = QuoteRequest.objects.filter(
                        user=result.user,
                        status=QuoteRequestStatus.accepted
                    ).count()
                    if accepted_count >= 5 and accepted_count % 5 == 0:
                        user_points, _ = UserPoints.objects.get_or_create(user=result.user)
                        user_points.total_points += 500
                        user_points.save()
                        
                return Response({
                    'message': 'Quote request created successfully',
                 }, status=status.HTTP_201_CREATED)
            except Property.DoesNotExist:
                return Response({'error': 'Property not found'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Failed to create quote request'}, status=status.HTTP_400_BAD_REQUEST)

class ListQuotesForPropertyView(ListAPIView):
    """
    Returns all QuoteRequest objects linked to a given Property.
    """
    serializer_class = QuoteRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        property_id = self.kwargs.get("property_id")
        if property_id is None:
            raise ValidationError("Property ID is required.")
        return QuoteRequest.objects.filter(property_id=property_id)
    
    
class ReturnedQuotes(ListAPIView):
    permission_classes = [IsAuthenticated] 
    serializer_class = QuoteRequestSerializer
     
    def get_queryset(self):
        return QuoteRequest.objects.filter(user = self.request.user, status = "returned")


class AcceptOrRejectQuotes(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = QuoteRequestSerializer
     
    def get_object(self):
        quote_id = self.kwargs.get("id")
        request_type = self.kwargs.get("request_type")
        if request_type == "accept":
            quote =   QuoteRequest.objects.get(id = quote_id)
            quote.status ='accepted'
            quote.save()
            return Response("Quote accepted", status=status.HTTP_200_OK)
        elif request_type == "reject":
            quote =   QuoteRequest.objects.get(id = quote_id)
            quote.status ='rejected'
            quote.save()


 



