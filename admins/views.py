from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Case, When, CharField
from django.db.models import Q


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count, Case, When
from quotes.serializers import QuoteRequestAllSerializer,ProjectSerializer
from quotes.models import Project, QuoteRequest, QuoteRequestStatus
from rest_framework.generics import GenericAPIView, ListAPIView, UpdateAPIView, RetrieveUpdateAPIView
from profiles.serializers import ContractorSerializer, HomeOwnerSerializer, AgentSerializer
from profiles.models import UserProfile, ContractorProfile, AgentProfile
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse as api_reverse
from django.http import Http404
from .serializer import UpdateContractorProfileSerializer,UpdateHomeOwnerSerializer,UpdateAgentSerializer
from django.shortcuts import get_object_or_404




User = get_user_model()


class AdminDashboardAPIView(GenericAPIView):
    """
    API View for Admin Dashboard.
    only admins can access it
    """
    permission_classes = [IsAuthenticated]

    
    def get(self, request, *args, **kwargs):
        print("onyeka")
        # Ensure only admin users can access this
        if request.user.user_type in ['HO', 'AG', 'CO']:
            return Response({'error': 'Unauthorized access'}, status=status.HTTP_403_FORBIDDEN)
        
        # Aggregations
        counts = User.objects.aggregate(
            home_owner_count=Count(Case(When(user_type='HO', then=1))),
            agent_count=Count(Case(When(user_type='AG', then=1))),
            contractor_count=Count(Case(When(user_type='CO', then=1))),
        )
        active_projects = Project.objects.filter(is_approved=True).count()

        # Recent Data
        recent_home_owners = User.objects.filter(user_type='HO').order_by('-id')[:4]
        recent_agents = User.objects.filter(user_type='AG').annotate(
            total_projects=Count('assigned_properties_to__assigned_by__quote_requests__quote_project'),
        ).order_by('-id')[:4]
        recent_contractors = User.objects.filter(user_type='CO').order_by('-id')[:4]
        recent_quote_requests = QuoteRequest.objects.select_related("user").order_by('-id')[:4]

        serialized_recent_home_owners = HomeOwnerSerializer(recent_home_owners, many=True).data
        serialized_recent_agents = AgentSerializer(recent_agents, many=True).data
        serialized_recent_contractors = ContractorSerializer(recent_contractors, many=True).data
        serialized_recent_quote_requests= QuoteRequestAllSerializer(recent_quote_requests, many=True).data

        overall_stats = [
            {'title':'Home Owners', 'project_counts': counts['home_owner_count'], 'action':'View owners', 'link' : api_reverse('admins:homeowners', request=request) },
            {'title':'Agents', 'project_counts': counts['agent_count'], 'action':'View agents', 'link' : api_reverse('admins:agents', request=request)},
            {'title':'Contractors', 'project_counts': counts['contractor_count'], 'action':'View contractors', 'link' : api_reverse('admins:contractors', request=request)},
            {'title':'Active Projects', 'project_counts': active_projects, 'action':'View projects', 'link' : api_reverse('admins:active-projects', request=request)},
        ]
        data = {
            'counts': counts,
            'active_projects': active_projects,
            'recent_home_owners': serialized_recent_home_owners,
            'recent_agents': serialized_recent_agents,
            'recent_contractors': serialized_recent_contractors,
            'recent_quote_requests': serialized_recent_quote_requests,
            'overall_stats': overall_stats,
        }

        return Response(data, status=status.HTTP_200_OK)


class ContractorsListAPIView(ListAPIView):
    """
    API View for listing contractors with pagination and search.
    """
    serializer_class = ContractorSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]
 


    def get_queryset(self):
        queryset = User.objects.filter(user_type='CO').select_related("contractor_profile").order_by('-id')
        query = self.request.GET.get('q')      
        if query:
            return queryset.filter(
                Q(contractor_profile__company_name__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset


class HomeOwnersListAPIView(ListAPIView):
    """
    API View for listing homeowners with pagination and search.
    """
    serializer_class = HomeOwnerSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = User.objects.filter(user_type='HO').select_related("user_profile").prefetch_related('quote_requests').order_by('-id')
        query = self.request.GET.get('q')
        if query:
            return queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(user_profile__city__icontains=query) |
                Q(user_profile__state_province__icontains=query) |
                Q(email__icontains=query)
            )
        return queryset


class AgentsListAPIView(ListAPIView):
    """
    API View for listing agents with pagination and search.
    """
   
    serializer_class = AgentSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = User.objects.filter(user_type='AG').select_related("user_profile").annotate(
            total_projects=Count('assigned_properties_to__assigned_by__quote_requests__quote_project'),
        ).order_by('-id')
        query = self.request.GET.get('q')
        if query:
            return queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(user_profile__city__icontains=query) |
                Q(user_profile__state_province__icontains=query) |
                Q(email__icontains=query) 
            )
        return queryset


class ProjectRequestListAPIView(ListAPIView):
    """
    API View for listing quote requests with pagination.
    """
    serializer_class = QuoteRequestAllSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = QuoteRequest.objects.all().order_by('-id')
        query = self.request.GET.get('q')
        if query:
            return queryset.filter(
                Q(user__first_name__icontains=query) |
                Q(user__last_name__icontains=query) |
                Q(title__icontains=query)
            )
        return queryset


class ProjectRequestDetailAPIView(APIView):
    """
    API View to handle the details of a specific project request.

    """
    permission_classes = [IsAuthenticated]


    def get(self, request, id):
        """
        Handle GET request to retrieve details of a specific QuoteRequest.
        """
        try:
            quote_request = QuoteRequest.objects.get(id=id)
        except QuoteRequest.DoesNotExist:
            return Response({'error': 'Quote Request not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the quote request data and return it
        serializer = QuoteRequestAllSerializer(quote_request)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request, id):
        try:
            quote_request = QuoteRequest.objects.get(id=id)
        except QuoteRequest.DoesNotExist:
            return Response({'error': 'Quote Request not found'}, status=status.HTTP_404_NOT_FOUND)

        decision = request.data.get('decision')
        if decision == "accept":
            pdf = request.FILES.get('pdf')
            Project.objects.create(
                admin=request.user,
                quote_request=quote_request,
                file=pdf,
                is_approved=True
            )
            quote_request.status = QuoteRequestStatus.approved
            quote_request.save(update_fields=['status'])

        elif decision == "reject":
            quote_request.status = QuoteRequestStatus.rejected
            quote_request.save(update_fields=['status'])
        
        return Response({'message': 'Project Request Updated'}, status=status.HTTP_200_OK)


class ActiveProjectListAPIView(ListAPIView):
    """
    API View for listing active projects with pagination and search.
    """
    serializer_class = ProjectSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        queryset = Project.objects.filter(is_approved=True).select_related('quote_request').order_by('-id')
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(quote_request__user__first_name__icontains=query) |
                Q(quote_request__user__last_name__icontains=query) |
                Q(quote_request__title__icontains=query)
            )
        return queryset
    

# class ChangeQuoteStatusAPIView(UpdateAPIView):
#     """
#     API View to change the status of a quote.
#     """
#     permission_classes = [IsAuthenticated]
#     serializer_class = QuoteStatusSerializer 
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         try:
#             return QuoteRequest.objects.get(pk=self.kwargs.get('pk'))
#         except QuoteRequest.DoesNotExist:
#             raise Http404("Quote not found")

#     def update(self, request, *args, **kwargs):
#         quote = self.get_object()
#         serializer = self.get_serializer(data=request.data)
#         if serializer.is_valid():
#             state = serializer.validated_data.get('status')
#             if str(state).lower() == "approved":
#                 Project.objects.get_or_create(
#                     admin=request.user,
#                     quote_request=quote,
#                     is_approved=True
#                 )
#             else:
#                 project = Project.objects.filter(quote_request=quote, is_approved=True).first()
#                 if project:
#                     project.delete()
                    
#             quote.status = state
#             quote.save()
#             return Response({'message': 'Quote status updated'}, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateContractorAPIView(RetrieveUpdateAPIView):
    """
    API View to update contractor profiles.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateContractorProfileSerializer  
    permission_classes = [IsAuthenticated]

    def get_object(self):
        contractor_profile = ContractorProfile.objects.select_related('user').get(id=self.kwargs.get('pk'))
        return contractor_profile.user
    
    # def get_serializer(self, *args, **kwargs):
    # to get the pk in the serializer
    #     # Add the pk from the URL to the serializer's context
    #     kwargs['context'] = self.get_serializer_context()
    #     kwargs['context']['pk'] = self.kwargs.get('pk')
    #     return super().get_serializer(*args, **kwargs)
    
    # to refresh the data, so as to get the current data, as i was getting the old data
    def update(self, request, *args, **kwargs):
        # Perform the update using the default update process
        super().update(request, *args, **kwargs)

        # Refresh the User instance from the database to get the updated data
        self.get_object().refresh_from_db()

        # Refresh the related ContractorProfile instance to get the updated data
        contractor_profile = ContractorProfile.objects.get(user=self.get_object())
        contractor_profile.refresh_from_db()

        # Serialize the updated User and ContractorProfile
        serializer = self.get_serializer(self.get_object())

        # Return the updated data in the response
        return Response(serializer.data)


class UpdateHomeOwnerAPIView(RetrieveUpdateAPIView):
    """
    API View to update homeowner profiles.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateHomeOwnerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        home_owner = get_object_or_404(UserProfile.objects.select_related('user'), id=self.kwargs.get('pk'))

        return home_owner.user


class UpdateAgentAPIView(RetrieveUpdateAPIView):
    """
    API View to update agent profiles.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = UpdateAgentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        agent_profile = get_object_or_404(AgentProfile.objects.select_related('user'), id=self.kwargs.get('pk'))
        return agent_profile.user 

