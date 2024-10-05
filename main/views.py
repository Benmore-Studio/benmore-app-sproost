from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from .forms import AgentAssignmentForm

from mail_templated import send_mail
from quotes.models import QuoteRequest, Project
from property.models import AssignedAccount
from profiles.models import AgentProfile, Referral
from django.contrib.auth.mixins import LoginRequiredMixin
from utils.views import get_base_url

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .serializers import AgentAssignmentSerializer
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from quotes.serializers import QuoteRequestAllSerializer, ProjectSerializer
from property.serializers import AssignedAccountSerializer






from django.urls import reverse

User = get_user_model()

def get_base_url(request):
    # Use 'get_current_site' to get the domain
    domain = get_current_site(request).domain
    # Use 'request.is_secure' to determine the scheme (http or https)
    scheme = 'https' if request.is_secure() else 'http'
    # Construct the base URL
    base_url = f"{scheme}://{domain}"
    return base_url

loggedInUser = 'contractor'

# general function to be called in other functions
def home_owner_function(request, value):
    quotes = QuoteRequest.objects.filter(user=value)
    projects = Project.objects.filter(quote_request__user=value)
    projs = Project.objects.filter(admin=value)
    context ={
        "quotes": quotes,
        "projects": projects,
        'projs':projs,
        "quote_count": quotes.count(),
        "projects_count": projects.count(),
        "home_owner_slug": request.user.slug
    }
    return context

# the vieew to route the home owner with slug
class HomeOwnerWithSlugNameView(APIView):
    """
    Retrieves home owner details using slug and returns their projects and quotes.

    ----------------------------
    INPUT PARAMETERS:
    - name: str (slug of the user)

    -----------------------------
    OUTPUT PARAMETERS:
    Returns home owner data and associated projects and quotes.
    """
    
    @extend_schema(
        responses={
            200: OpenApiResponse(description="Homeowner data and associated projects and quotes"),
            404: OpenApiResponse(description="Homeowner not found"),
        }
    )

    def get(self, request, name, *args, **kwargs):
        user = get_object_or_404(User, slug=name)
        context = home_owner_function(request, user)
        context['name'] = name
        return Response(context, status=status.HTTP_200_OK)


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
        if not request.user.is_authenticated:
            return redirect('account_login')

        user_type = request.user.user_type
        if user_type == "HO":
            context = home_owner_function(request, request.user)
            return Response(context)
        elif user_type == "CO":
            return redirect("profile:contractor_profile")
        elif user_type == "AG":
            URL = get_base_url(request)
            quotes = QuoteRequest.objects.filter(created_by_agent=request.user)
            projects = Project.objects.filter(quote_request__user=request.user)
            proj = Project.objects.filter(admin=request.user)
            accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related("assigned_by", "assigned_to")
            agent = User.objects.get(pk=request.user.pk)
            agent_profile = AgentProfile.objects.get(user=agent)

            serialized_quotes = QuoteRequestAllSerializer(quotes, many=True).data
            serialized_projects = ProjectSerializer(projects, many=True).data
            serialized_proj = ProjectSerializer(proj, many=True).data
            serialized_accounts = AssignedAccountSerializer(accounts, many=True).data

            referral, created = Referral.objects.get_or_create(referrer=request.user)
            if created:
                if agent_profile.registration_ID:
                    referral.code = agent_profile.registration_ID
                    referral.save()

            signup_url = reverse('account_signup')
            referral_link = request.build_absolute_uri(f'{signup_url}?ref={referral.code}')
            context = {
                "quote_count": quotes.count(),
                "projects_count": projects.count(),
                "accounts": accounts,
                "accounts_len": len(accounts),
                'url': URL,
                'proj': proj,
                'quotes': quotes,
                'referral_link': referral_link
            }
            return Response(context, status=status.HTTP_200_OK)
        else:
            return redirect("admins:dashboard")


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
        if not request.user.is_authenticated:
            return redirect('account_login')

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




# the vieew to route the home owner with slug
def home_owner_with_slug_name(request, name):
    user = User.objects.get(slug=name)
    context = home_owner_function(request, user)
    context['name'] = name
    return render(request, "user/home.html", context)


# mains

def home(request):
    if not request.user.is_authenticated:
        return redirect('account_login')
    else:
        if request.user.user_type == "HO":
            context = home_owner_function(request, request.user)
            return render(request, "user/home.html", context)
        elif request.user.user_type == "CO":
            return redirect("profile:contractor_profile")
        elif request.user.user_type == "AG":
            URL = get_base_url(request)
            quotes = QuoteRequest.objects.filter(created_by_agent=request.user) 
            projects = Project.objects.filter(quote_request__user=request.user)
            proj = Project.objects.filter(admin=request.user)
            accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related(
                "assigned_by", "assigned_to")
            # print(projects)
            agent = User.objects.get(pk=request.user.pk)
            agent_profile = AgentProfile.objects.get(user=agent)
            referral, created = Referral.objects.get_or_create(referrer=request.user)
            if created:
                if agent_profile.registration_ID:
                    referral.code = agent_profile.registration_ID
                    referral.save()

            signup_url = reverse('account_signup')
            referral_link = request.build_absolute_uri(f'{signup_url}?ref={referral.code}')
            context = {
                "quote_count": quotes.count(),
                "projects_count": projects.count(),
                "accounts": accounts,
                "accounts_len": len(accounts),
                'url':URL,
                'proj':proj,
                'quotes':quotes,
                # 'onboarding_message': agent_profile.has_seen_onboarding_message,
                'referral_link': referral_link
            }
            return render(request, "user/agent_home.html", context)
        else:
            return redirect("admins:dashboard")
        
def Assigned_projects(request):
    if not request.user.is_authenticated:
        return redirect('account_login')

    else:
        quotes = QuoteRequest.objects.filter(user=request.user)
        projects = Project.objects.filter(quote_request__user=request.user)
        proj = Project.objects.filter(admin=request.user)
        accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related(
            "assigned_by", "assigned_to")

        context = {
            "quote_count": quotes.count(),
            "projects_count": projects.count(),
            "accounts": accounts,
            'proj':proj,
            "accounts_len": len(accounts),
            
        }
        return render(request, "user/agent_assignor.html", context)
       

class AssignAgentView(LoginRequiredMixin, View):
    template_name = 'user/assignAgent.html'
    form_class = AgentAssignmentForm

    def get(self, request):
        if not request.user.user_type == 'HO':
            return redirect('main:home')
        
        agents = User.objects.filter(user_type='AG')
        context = {
            'agents': agents,
            'form' : self.form_class()
        }
        return render(request, self.template_name, context)

    def post(self, request):
        
        form = self.form_class(request.POST)
        if form.is_valid():
            regID = form.cleaned_data.get('registration_id')
            try:
                
                agent = AgentProfile.objects.get(registration_ID=regID)
                if AssignedAccount.objects.filter(assigned_by=request.user, assigned_to=agent.user).exists():
                    messages.warning(request, 'Agent already assigned. Awaiting agent confirmation')
                    return redirect('main:assign-agent')
                
                AssignedAccount.objects.get_or_create(
                    assigned_to=agent.user,
                    assigned_by=request.user,
                    is_approved=True
                )
                # send_mail(
                #     'mail/assign_agent.tpl',
                #     {'first_name': agent.user.first_name, "base_url": get_base_url(request)},
                #     settings.EMAIL_HOST_USER,
                #     [agent.user.email]
                # )

                messages.success(request, 'Agent assigned successfully. Awaiting agent confirmation')
                return redirect('main:home')
            except AgentProfile.DoesNotExist:
                messages.error(request, f'No Agent exists with such liscense ID: {regID}')
        else:
            pass
        return redirect('main:assign-agent')



# unused functions
# def homeOwners(request):
#     project_feed = [
#         {
#             'title': 'Number of Uploaded projects', 'status': 'uploaded', 'count': 3,
#         },
#         {
#             'title': 'Number of Quotes Requested', 'status': 'quotes', 'count': 3,
#         },
#         {
#             'title': 'Number of completed projects', 'status': 'completed', 'count': 0,
#         }
#     ]

#     project_history = [
#         {'name': 'Bungalow Renovation', 'quotation_status': 'pending',
#          'home_owner': {'name': 'Olivia Rhye', 'image': '/static/images/ownerAvatar.png'},
#          'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
#         {'name': 'Bungalow Renovation', 'quotation_status': 'pending',
#          'home_owner': {'name': 'Olivia Rhye', 'image': '/static/images/ownerAvatar.png'},
#          'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
#         {'name': 'Bungalow Renovation', 'quotation_status': 'pending',
#          'home_owner': {'name': 'Olivia Rhye', 'image': '/static/images/ownerAvatar.png'},
#          'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
#     ]

#     context = {'project_feed': project_feed, 'project_history': project_history, 'loggedInUser': loggedInUser}
#     return render(request, 'user/home.html', context)



# def requestQuotes(request):
#     context = {
#         'loggedInUser': loggedInUser
#     }
#     return render(request, 'user/request_quotes.html', context)

 
def QuotationReturn(request):
    context = {
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/quotation_returns.html', context)


def MenuList(request):
    context = {
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/menu.html', context)


def contractors(request):
    searchResults = [
        {'name': 'Olivia Rhye', 'profession': 'plumber', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Phoenix Baker', 'profession': 'electrician', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
        {'name': 'Lana Steiner', 'profession': 'carpenter', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
        {'name': 'Demi Wilkinson', 'profession': 'interior designer', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
        {'name': 'Candice Wua', 'profession': 'painter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Natali Craig', 'profession': 'carpenter', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
        {'name': 'Drew Cano', 'profession': 'painter', 'phone': '+1 834 955 0920', 'email': 'olivia@untitledui.com'},
        {'name': 'Phoenix Baker', 'profession': 'electrician', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
        {'name': 'Lana Steiner', 'profession': 'carpenter', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
        {'name': 'Demi Wilkinson', 'profession': 'interior designer', 'phone': '+1 834 955 0920',
         'email': 'olivia@untitledui.com'},
    ]
    context = {
        'contractors': searchResults,
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/contractors.html', context)


def contractorDetail(request, profession):
    context = {
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/contractorDetail.html', context)


