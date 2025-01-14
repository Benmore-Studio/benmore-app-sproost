from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.services.user import UserService
from django.views.generic import View
from django.contrib import messages
from services.utils import CustomRequestUtil
from quotes.services import QuoteService

from rest_framework import viewsets
from .models import Project, Property, QuoteRequest
from .serializers import ProjectSerializer, QuoteRequestSerializer, PropertySerializer, MediaSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from profiles.models import UserProfile, AgentProfile

from django.db.models import Prefetch

from django.core.serializers import serialize




import json

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer




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


    def post(self, request, *args, **kwargs):
        """
        Handle POST request to submit quote request data, including media files.
        """
        user = request.user
        if not user.is_authenticated:  # Check if the user is authenticated
            return self.handle_no_permission()

        # Initialize the serializer with data from the request
        if request.user.user_type == "HO" or request.user.user_type == "AG":
            user_profile = self.get_user(user)
        else:
            return Response({"error": "user not allowed to upload"}, status=status.HTTP_400_BAD_REQUEST)
        data_copy = request.data.copy()
        data_copy['property_owner'] = user_profile.id
        print("data_copy",data_copy)
        serializer = self.get_serializer(data=data_copy) 
        if serializer.is_valid():
            form_data = serializer.validated_data
            # form_data['user'] = user
            # form_data['associated_user'] = user

            # Handle media file uploads
            form_data['media'] = None
            if 'media' in request.FILES:
                uploaded_files = request.FILES.getlist("media")
                form_data["media"] = uploaded_files

            # Process the quote request using the QuoteService
            user_profile = self.get_user(user)
            quote_service = QuoteService(request, user_profile)
            result, error = quote_service.create(form_data, user_profile, model_passed=Property)

            # serializer = MediaSerializer()
            # created_media, errors = serializer.create_many(content_type, object_id, files, images, videos)

            # if errors:
            #     event.delete()
            #     return Response({"error": errors}, status=status.HTTP_400_BAD_REQUEST)

            if result:
                return Response({'message': 'request successfull',
                                #  "result":json.loads(result),
                                 }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Request unsuccessful'}, status=status.HTTP_400_BAD_REQUEST)
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
        user_quotes = self.get_user(user)
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
        if not user.is_authenticated:  # Check if the user is authenticated
            return self.handle_no_permission()
        
        home_owner_id = kwargs.get("id")


        if home_owner_id:
            # Fetch home owner by ID
            user = get_object_or_404(User, pk=home_owner_id)

        initial_data = self.get_initial_data(user)
        return Response(initial_data, status=status.HTTP_200_OK)


    def post(self, request, *args, **kwargs):
        """
        Handle POST request to submit quote request data, including media files.
        """
        # home_owner_id = kwargs.get("name")
        user = request.user
        if not user.is_authenticated:  # Check if the user is authenticated
            return self.handle_no_permission()

        # Initialize the serializer with data from the request
        serializer = self.get_serializer(data=request.data) 
        if serializer.is_valid():
            form_data = serializer.validated_data
            form_data['user'] = user
            # form_data['associated_user'] = user

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



# class Quotes(LoginRequiredMixin, View, CustomRequestUtil):
#     template_name = "user/request_quotes.html"
#     extra_context_data = {}
#     form_class = QuoteRequestForm

#     def get_initial_data(self):
#         if self.user.user_type == 'HO':
#             return {
#                 'contact_username': self.user.username,
#                 'contact_phone': self.user.phone_number,
#                 'property_address': self.user.user_profile.address,
#                 'custom_home_owner_id': self.request.user.pk,
#                 'created_by_agent': self.request.user.pk
#             }
#         elif self.user.user_type == 'AG':
#             return {
#                 'contact_username': self.user.username,
#                 'contact_phone': self.user.phone_number,
#                 'property_address': self.user.agent_profile.address
#             }

#     def get(self, request, *args, **kwargs):
#         home_owner_id = kwargs.get("id")
#         self.user = self.auth_user

#         if home_owner_id:
#             user_service = UserService(request)
#             self.user, error = user_service.fetch_single_by_pk(id=home_owner_id)

#             if error:
#                 messages.error(request, error)
#                 return redirect('main:home')
        
#         initial_data = self.get_initial_data()
#         form = self.form_class(initial=initial_data)
#         self.extra_context_data = {
#             "loggedInUser": f"{UserTypes.contractor}",
#             "form": form
#         }
        
#         return self.process_request(request)
    
#     def post(self, request, *args, **kwargs):
#         self.user = self.auth_user
#         home_owner_id = kwargs.get("name")
#         self.template_name = None
#         initial_data = self.get_initial_data()
#         form = self.form_class(request.POST, request.FILES)

#         if home_owner_id:
#             self.template_on_error = ("quotes:request-quotes", home_owner_id)
#         else:
#             self.template_on_error = "quotes:request-quotes"

#         if form.is_valid():
#             form_data = form.cleaned_data

#             # if home_owner_id:
#             #     user = User.objects.get(slug=home_owner_id)
#             #     form_data["created_by_agent"] = request.user
#             #     form_data["user"] = user
#             # else:
#             #     form_data["user"] = request.user
#             #     form_data["created_by_agent"] = None

#             form_data["user"] = request.user
#             form_data['media'] = None
#             if request.FILES:
#                 uploaded_files = request.FILES.getlist("media")
#                 form_data["media"] = uploaded_files
#             quote_service = QuoteService(request)
#             return self.process_request(request, target_view="main:home", target_function=quote_service.create, payload=form_data)

#         else:
#             self.extra_context_data["form"] = form
#             for field, errors in form.errors.items():
#                 for error in errors:
#                     messages.error(self.request, f"{error}")
#             form = self.form_class(initial=initial_data, data=request.POST)
#             return render(request, 'user/request_quotes.html', {'form': form})




