from quotes.models import Project, QuoteRequest
from django.contrib.auth import get_user_model
from .models import AssignedAccount, Property
from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, PermissionDenied
from profiles.serializers import HomeOwnerSerializer 
from .serializers import ( PropertyCreateSerializer,PropertyUpdateSerializer, PropertyRetrieveSerializer)
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, filters
from django.shortcuts import get_object_or_404



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



class PropertyListAPIView(generics.ListAPIView):
    """
    API View to retrieve all properties with search and filter options.
    """
    queryset = Property.objects.all()
    serializer_class = PropertyRetrieveSerializer
    filter_backends = [filters.SearchFilter]  # Only search, no filtering
    search_fields = ['title', 'address', 'property_type', 'status']    
    # Fields that can be searched using ?search=
    
    def get_queryset(self):
        """
        Get properties for a specific user if `user_id` is provided in query params.
        Otherwise, return all properties.
        """
        queryset = Property.objects.all()
        user_id = self.request.query_params.get('user_id')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            queryset = queryset.filter(property_owner=user)

        return queryset
 



class UserPropertyListView(generics.ListAPIView):
    serializer_class = PropertyRetrieveSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_type = getattr(user, 'user_type', None)
        
        # Start with an empty QuerySet.
        qs = Property.objects.none()

        if user_type == "CO":
            # For contractors, combine properties they own and those assigned to their contractor profile.
            qs = Property.objects.filter(property_owner=user)
            try:
                contractor_profile = user.contractor_profile  # Adjust attribute name if needed.
                qs = qs | Property.objects.filter(contractors=contractor_profile)
            except Exception:
                pass
        elif user_type == "AG":
            # For agents, include properties they own and those where they are added as a home_owner_agent.
            qs = Property.objects.filter(Q(property_owner=user) | Q(home_owner_agents=user))
        elif user_type == "HO":
            # For home owners, only include properties they own.
            qs = Property.objects.filter(property_owner=user)
        elif user_type == "IV":
            # For investors, you might choose a different rule. Here we return properties they liked.
            qs = Property.objects.filter(likes=user)
        else:
            # For any other user type, you might default to all properties.
            qs = Property.objects.all()

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