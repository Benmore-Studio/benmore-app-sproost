from quotes.models import Project, QuoteRequest
from django.contrib.auth import get_user_model
from .models import AssignedAccount
from quotes.models import Property
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from property.models import AssignedAccount
from profiles.serializers import HomeOwnerSerializer 
from .serializers import ( PropertyCreateSerializer,PropertyUpdateSerializer, PropertyRetrieveSerializer)
from rest_framework.parsers import MultiPartParser, FormParser


User = get_user_model()


class AgentsHomeOwnerAccountAPIView(generics.RetrieveAPIView):
    """
    API View to handle retrieving a home owner's details for agents who were assigned to them.

    ----------------------------
    INPUT PARAMETERS:
    - pk: int (Primary key of the home owner)

    -----------------------------
    OUTPUT PARAMETERS:
    Returns home owner data, assigned quotes, and projects.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = HomeOwnerSerializer

    def get(self, request, pk, *args, **kwargs):
        try:
            home_owner = User.objects.get(pk=pk)

            # Check if the agent is assigned to this home owner
            if not AssignedAccount.objects.filter(assigned_by=home_owner, assigned_to=request.user).exists():
                raise PermissionDenied(f"You were not assigned by {home_owner.email} to view their account.")

            # Fetch related quotes and projects for the home owner
            quotes = QuoteRequest.objects.filter(user=home_owner)
            projects = Project.objects.filter(quote_request__user=home_owner)

            # Create the context data for the response
            context = {
                "home_owner": {
                    "id": home_owner.id,
                    "email": home_owner.email,
                    "first_name": home_owner.first_name,
                    "last_name": home_owner.last_name,
                },
                "quotes": quotes.values(),  # Returns all the quotes as a list of dictionaries
                "projects": projects.values(),  # Returns all the projects as a list of dictionaries
                "quote_count": quotes.count(),
                "projects_count": projects.count(),
            }

            return Response(context, status=200)

        except User.DoesNotExist:
            raise NotFound("Home Owner not found.")

        
class PropertyCreateView(generics.CreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyCreateSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]



   
    
class PropertyRetrieveView(generics.RetrieveAPIView):
    queryset = Property.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PropertyRetrieveSerializer

class PropertyUpdateView(generics.UpdateAPIView):
    queryset = Property.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = PropertyUpdateSerializer




class ContractorAllPropertiesView(generics.ListAPIView):
    serializer_class = PropertyRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # Query for properties owned by the user.
        qs = Property.objects.filter(property_owner=user)
        # If the user has a contractor profile, include properties assigned to that profile.
        try:
            contractor_profile = user.contractor_profile
            qs = qs | Property.objects.filter(contractors=contractor_profile)
        except Exception:
            # No contractor profile; do nothing extra.
            pass

        return qs.distinct()
    
    
class PropertyDeleteView(generics.DestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertyRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        request = self.request
        # Only allow deletion if the request.user is the property owner or an admin.
        if instance.property_owner != request.user and not request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You do not have permission to delete this property.")
        instance.delete()