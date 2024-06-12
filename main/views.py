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

from django.urls import reverse


from decouple import config

User = get_user_model()

# general function to be called in other functions
def home_owner_function(request, value):
    quotes = QuoteRequest.objects.filter(user=value)
    projects = Project.objects.filter(quote_request__user=value)
    context ={
        "quotes": quotes,
        "projects": projects,
        "quote_count": quotes.count(),
        "projects_count": projects.count(),
        "home_owner_slug": request.user.slug
    }
    return context

# the vieew to route the home owner with slug
def home_owner_with_slug_name(request, name):
    user = User.objects.get(slug=name)
    context = home_owner_function(request, user)
    context['name'] = name
    return render(request, "user/home.html", context)

def get_base_url(request):
    # Use 'get_current_site' to get the domain
    domain = get_current_site(request).domain
    # Use 'request.is_secure' to determine the scheme (http or https)
    scheme = 'https' if request.is_secure() else 'http'
    # Construct the base URL
    base_url = f"{scheme}://{domain}"
    return base_url


loggedInUser = 'contractor'


# mains
def homeOwners(request):
    project_feed = [
        {
            'title': 'Number of Uploaded projects', 'status': 'uploaded', 'count': 3,
        },
        {
            'title': 'Number of Quotes Requested', 'status': 'quotes', 'count': 3,
        },
        {
            'title': 'Number of completed projects', 'status': 'completed', 'count': 0,
        }
    ]

    project_history = [
        {'name': 'Bungalow Renovation', 'quotation_status': 'pending',
         'home_owner': {'name': 'Olivia Rhye', 'image': '/static/images/ownerAvatar.png'},
         'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name': 'Bungalow Renovation', 'quotation_status': 'pending',
         'home_owner': {'name': 'Olivia Rhye', 'image': '/static/images/ownerAvatar.png'},
         'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
        {'name': 'Bungalow Renovation', 'quotation_status': 'pending',
         'home_owner': {'name': 'Olivia Rhye', 'image': '/static/images/ownerAvatar.png'},
         'location': 'New Yersey, Newark', 'created_date': 'Jan 28, 2024'},
    ]

    context = {'project_feed': project_feed, 'project_history': project_history, 'loggedInUser': loggedInUser}
    return render(request, 'user/home.html', context)


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
            URL = config('UPDATEURL')
            quotes = QuoteRequest.objects.filter(created_by_agent=request.user) 
            projects = Project.objects.filter(quote_request__user=request.user)
            accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related(
                "assigned_by", "assigned_to")
            agent = User.objects.get(pk=request.user.pk)
            agent_profile = AgentProfile.objects.get(user=agent)
            referral, created = Referral.objects.get_or_create(referrer=request.user)
            if created:
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
                'quotes':quotes,
                'onboarding_message': agent_profile.has_seen_onboarding_message,
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
        accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related(
            "assigned_by", "assigned_to")

        context = {
            "quote_count": quotes.count(),
            "projects_count": projects.count(),
            "accounts": accounts,
            "accounts_len": len(accounts),
            
        }
        return render(request, "user/agent_assignor.html", context)
       
# def home(request):

#     if loggedInUser == 'agent':
#         context = {
#         'loggedInUser': loggedInUser
#     }
#         return render(request, 'user/agent_home.html', context)
#     else:
#         return homeOwners(request)


def requestQuotes(request):
    context = {
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/request_quotes.html', context)


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
                send_mail(
                    'mail/assign_agent.tpl',
                    {'first_name': agent.user.first_name, "base_url": get_base_url(request)},
                    settings.EMAIL_HOST_USER,
                    [agent.user.email]
                )

                messages.success(request, 'Agent assigned successfully. Awaiting agent confirmation')
                return redirect('main:home')
            except AgentProfile.DoesNotExist:
                messages.error(request, f'No Agent exists with such liscense ID: {regID}')

        return redirect('main:assign-agent')



# unused functions

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


