from django.contrib.auth import get_user_model

from quotes.models import QuoteRequest, Project
from property.models import AssignedAccount
from profiles.views import get_user_data
from profiles.models import AgentProfile, UserProfile, ContractorProfile
from profiles.serializers import HomeOwnerSerializer,AgentSerializer,ContractorSerializer, ContractorProfileSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import RetrieveAPIView,GenericAPIView, RetrieveUpdateAPIView, ListAPIView
from rest_framework.test import APIRequestFactory
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiResponse


from django.shortcuts import get_object_or_404
from .serializers import AgentAssignmentSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from quotes.serializers import QuoteRequestAllSerializer, ProjectSerializer
from property.serializers import AssignedAccountSerializer

from profiles.models import Referral





from django.urls import reverse

User = get_user_model()


loggedInUser = 'contractor'

# general function to be called in other functions
        



class HomeView(GenericAPIView):
    """
    Returns home data based on user type (Homeowner, Contractor, or Agent).

    ----------------------------
    INPUT PARAMETERS:
    - None

    -----------------------------
    OUTPUT PARAMETERS:
    Returns home-related data such as projects and quotes based on the user type.
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Home data for the authenticated user"),
            302: OpenApiResponse(description="Redirects if the user is not authenticated or other cases"),
        },
    )

    def get(self, request, *args, **kwargs):
        user = request.user
        user_type = user.user_type
    
        if user_type == "HO" or user_type == "AG":
            context = get_user_data(request)
            return Response(context, status=status.HTTP_200_OK)

        elif user_type == "CO":
            contractor_profile =  User.objects.select_related('contractor_profile') .prefetch_related(
                 'property_owner').get(id=request.user.id)
            serializer = ContractorSerializer(contractor_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise PermissionDenied("Unauthorized access")


class HomeViewByPkAPIView(RetrieveAPIView):
    """
    Retrieves user details using pk and returns their associated information based on user type.
    """
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Returns the appropriate serializer based on the user type.
        """
        user = self.get_user()

        if user.user_type == 'CO':
            return ContractorSerializer
        elif user.user_type == 'AG':
            return AgentSerializer
        elif user.user_type == 'HO':
            return HomeOwnerSerializer
        else:
            raise NotFound({"error": "User type not supported"})

    def get_user(self):
        """
        Helper method to get the user from the provided pk.
        """
        pk = self.kwargs.get('pk')
        profile_model = None

        # Determine the correct profile model based on user type
        if self.request.user.user_type == 'CO':
            profile_model = ContractorProfile
        elif self.request.user.user_type == 'AG':
            profile_model = AgentProfile
        elif self.request.user.user_type == 'HO':
            profile_model = UserProfile
        else:
            raise NotFound({"error": "User type not supported."})

        # Fetch the profile instance or raise a not found error
        try:
            profile_instance = profile_model.objects.select_related('user').get(pk=pk)
            return profile_instance.user

        except profile_model.DoesNotExist:
            raise NotFound({"error": "Profile not found."})

    def get_object(self):
        """
        Retrieves the appropriate user instance using the pk.
        """
        return self.get_user()

    def retrieve(self, request, *args, **kwargs):
        """
        Overridden to provide additional data like quote count and projects count.
        """
        user = self.get_object()
        
        if user.user_type == 'HO':
            quote_count = QuoteRequest.objects.filter(user=user).count()
            projects_count = Project.objects.filter(admin=user).count()
            serializer = self.get_serializer(user)

            response_data = serializer.data
            response_data.update({
                "quote_count": quote_count,
                "projects_count": projects_count,
                "home_owner_slug": user.slug
            })

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            # You can add similar logic for other user types
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)


class ContractorListAPIView(ListAPIView):
    """
    API View view all contractor profiles.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ContractorSerializer
    queryset = ContractorProfile.objects.all()




class AssignedProjectsView(APIView):
    """
    Returns data for assigned projects and related accounts.

    ----------------------------
    INPUT PARAMETERS:
    - None

    -----------------------------
    OUTPUT PARAMETERS:
    Returns assigned projects, quotes, and account information.
    """

    def get(self, request, *args, **kwargs):
        quotes = QuoteRequest.objects.filter(user=request.user)
        projects = Project.objects.filter(quote_request__user=request.user)
        proj = Project.objects.filter(admin=request.user)
        accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related(
            "assigned_by", "assigned_to"
        )

        context = {
            "quote_count": quotes.count(),
            "projects_count": projects.count(),
            "accounts": accounts,
            'proj': proj,
            "accounts_len": len(accounts),
        }
        return Response(context, status=status.HTTP_200_OK)



class AssignAgentAPIView(GenericAPIView):
    """
    Handles agent assignment for Homeowners.

    ----------------------------
    INPUT PARAMETERS:
    POST: {registration_id: str}

    -----------------------------
    OUTPUT PARAMETERS:
    Returns success or error messages upon assigning an agent.
    """
    serializer_class = AgentAssignmentSerializer
    permission_classes = [IsAuthenticated] 


    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            regID = serializer.validated_data.get('registration_ID')

            # Fetch the agent based on the registration_ID
            try:
                agent = AgentProfile.objects.get(registration_ID=regID).user  # Assuming `AgentProfile` has a `user` ForeignKey
            except AgentProfile.DoesNotExist:
                # 404 Not Found - No agent with the given registration_ID
                return Response({'error': f'No agent found with registration ID: {regID}'}, status=status.HTTP_404_NOT_FOUND)

            # Ensure that the `assigned_by` user is either a home owner ('HO') or agent ('AG')
            assigned_by = request.user
            if assigned_by.user_type not in ['HO', 'AG']:
                # 400 Bad Request - User attempting to assign is neither a home owner nor an agent
                return Response({'error': 'Only home owners or agents can assign agents'}, status=status.HTTP_400_BAD_REQUEST)

            # Ensure that the `assigned_to` user is an agent ('AG')
            if agent.user_type != 'AG':
                # 400 Bad Request - The assigned user is not an agent
                return Response({'error': 'Only agents can be assigned properties'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if this agent has already been assigned
            if AssignedAccount.objects.filter(assigned_by=assigned_by, assigned_to=agent).exists():
                # 400 Bad Request - Agent has already been assigned by this user
                return Response({'message': 'Agent has already been assigned'}, status=status.HTTP_400_BAD_REQUEST)

            # Create the `AssignedAccount` entry
            AssignedAccount.objects.create(
                assigned_to=agent,
                assigned_by=assigned_by,
                is_approved=True
            )

            # 201 Created - The agent was successfully assigned
            return Response({'message': 'Agent assigned successfully'}, status=status.HTTP_201_CREATED)

        # 400 Bad Request - Invalid data in the request
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


