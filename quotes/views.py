from django.shortcuts import get_object_or_404

from accounts.models import User
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiTypes
from quotes.services import QuoteService

from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status, filters
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated

from profiles.models import UserProfile, AgentProfile
from profiles.serializers import PropertySerializer
from .models import Project, Property, QuoteRequest
from .serializers import ProjectSerializer, QuoteRequestSerializer,BulkMediaSerializer, MediaSerializer

from django.db.models import Prefetch
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
import json


User = get_user_model()

class PropertyAPIView(GenericAPIView):
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

    send your request in this format-properties:{"tittle": "Sample Property",
    "address": "123 Sample St",
    "status": "pending",
    "home_owner_agents": [1, 2, 4]
    },
    images:image files, 
    videos:video inputs, 
    files(pdf):file_input
    """
    serializer_class = PropertySerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated] 
    # user_profile = UserProfile.objects.get(user= payload["user"])

    def get_user(self, user):
        return User.objects.prefetch_related(Prefetch('property_owner', queryset=Property.objects.all())).get(id=user.id)
  
    
    def get_initial_data(self, user):
        """
        Get initial data for the form based on the user type (HO or AG).
        """
        home_owner_properties = self.get_user(user)
        property_data = json.loads(serialize('json', home_owner_properties.property_owner.all()))
        if user.user_type == 'HO':
            return {
                'contact_phone': str(user.phone_number),
                'custom_home_owner_id': user.pk,
                'created_by_agent': user.pk,
                "property": property_data
            }
        elif user.user_type == 'AG':
            print("agent")
            return {
                'contact_phone': str(user.phone_number),
                'property':property_data
            }
        else:
            return {}



    def handle_no_permission(self):
        """
        Custom response for unauthenticated requests.
        """
        return Response({'error': 'You are not authenticated. Please log in and try again.'}, status=status.HTTP_401_UNAUTHORIZED)

    def get(self, request, *args, **kwargs):
        """
        Handle GET request to return initial form data.
        """
        user = request.user
        if not user.is_authenticated:  # Check if the user is authenticated
            return self.handle_no_permission()
        


        initial_data = self.get_initial_data(user)
        return Response(initial_data, status=status.HTTP_200_OK)


    @extend_schema(
        summary="Upload Property with Media Files",
        description="""
        Allows users to submit property data along with associated media files.

        **Required Fields:**
        - `properties` (JSON String): Property details including title, address, etc.
        - `images` (File): One or multiple image files.
        - `videos` (File): One or multiple video files.
        - `files` (File): PDFs or other document files.
        """,
        parameters=[
            OpenApiParameter(name="properties", type=OpenApiTypes.STR, required=True, description="Property details in JSON string."),
            OpenApiParameter(name="images", type=OpenApiTypes.STR, required=False, description="Multiple image files."),
            OpenApiParameter(name="videos", type=OpenApiTypes.STR, required=False, description="Multiple video files."),
            OpenApiParameter(name="files", type=OpenApiTypes.STR, required=False, description="Multiple document files (PDFs, etc.)."),
        ],
        
        responses={201: OpenApiTypes.OBJECT},
    )
    def post(self, request, *args, **kwargs):
        """
        Handle POST request to submit quote request data, including media files.
        """
        user = request.user
        if not user.is_authenticated: 
            return self.handle_no_permission()

        # Initialize the serializer with data from the request
        if request.user.user_type == "HO" or request.user.user_type == "AG":
            user_profile = self.get_user(user)
        else:
            return Response({"error": "user not allowed to upload"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_property = json.loads(request.data.get('properties'))
        except (TypeError, json.JSONDecodeError):
            return Response({"error": "Invalid JSON data"}, status=status.HTTP_400_BAD_REQUEST)
        
        user_property['property_owner'] = user_profile.id
        print("data_copy",user_property)
        serializer = self.get_serializer(data=user_property) 
        if serializer.is_valid():
            property_created = serializer.save()
            media_serializer={}
            if request.FILES:
                print("request.FILES", request.FILES)
                content_type = ContentType.objects.get_for_model(property_created)
                bulk_media_data = {
                    "content_type_id": content_type.id,
                    "object_id": property_created.id,
                    "files": request.FILES.getlist('files', []),
                    "images": request.FILES.getlist('images', []),
                    "videos": request.FILES.getlist('videos', []),
                }
                media_serializer = BulkMediaSerializer(data=bulk_media_data)
                if media_serializer.is_valid():
                    media_serializer.save() 
            return Response({'message': 'request successfull', "property":serializer.data}, status=status.HTTP_201_CREATED)
            
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



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
    # user_profile = UserProfile.objects.get(user= payload["user"])

    def get_user(self, user):
        return User.objects.prefetch_related(Prefetch('quote_requests', queryset=QuoteRequest.objects.all())).get(id=user.id)

    def get_initial_data(self, user):
        """
        Get initial data for the form based on the user type (HO or AG).
        """
        home_owner_quotes = self.get_user(user)
        quotes_data = json.loads(serialize('json', home_owner_quotes.quote_requests.all()))
        if user.user_type == 'HO':
            return {
                'contact_phone': str(user.phone_number),
                'custom_home_owner_id': user.pk,
                'created_by_agent': user.pk,
                "quotes": quotes_data
            }
        elif user.user_type == 'AG':
            return {
                'contact_phone': user.phone_number,
            }
        return {}


    def handle_no_permission(self):
        """
        Custom response for unauthenticated requests.
        """
        return Response({'error': 'You are not authenticated. Please log in and try again.'}, status=status.HTTP_401_UNAUTHORIZED)


    def get(self, request, *args, **kwargs):
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


    def post(self, request, *args, **kwargs):
        """
        Handle POST request to submit quote request data, including media files.
        """
        user = request.user
        if not user.is_authenticated:
            return self.handle_no_permission()

        # Initialize the serializer with data from the request
        if request.user.user_type == 'AG' or request.user.user_type == 'HO':
            data_copy = request.data.copy()
            data_copy['user'] = user.id
            serializer = self.get_serializer(data=data_copy) 
            if serializer.is_valid():
                form_data = serializer.validated_data
                form_data['user'] = user

                # Handle media file uploads
                form_data['media'] = None
                if 'media' in request.FILES:
                    uploaded_files = request.FILES.getlist("media")
                    form_data["media"] = uploaded_files

                # Process the quote request using the QuoteService
                print(request.data, "lord")
                # request_data = request.data.copy()
                user_profile = self.get_user(user)
                quote_service = QuoteService(request, user_profile)
                # print(quote_service)
                result, error = quote_service.create(form_data, user_profile, model_passed=QuoteRequest)

                if result:
                    return Response({'message': 'Quote request created successfully',
                                    #  "result":json.loads(result),
                                    }, status=status.HTTP_201_CREATED)
                else:
                    return Response({'error': 'Failed to create quote request'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                print(serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"errors":"User type not allowed to create quotes"}, status=status.HTTP_400_BAD_REQUEST)


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


class PropertySearchView(ListAPIView):
    """
    GET /api/properties/?search=<query>, 
    search_fields = ['address', 'property_owner__username', 'basement_details', 'tittle']
    """
    queryset = Property.objects.all().order_by("id")
    serializer_class = PropertySerializer
    filter_backends = [filters.SearchFilter]
    # Adjust these fields to whatever you want to enable searching on
    search_fields = ['address', 'property_owner__username', 'basement_details', 'tittle']
