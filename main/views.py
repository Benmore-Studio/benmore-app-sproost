from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site

from mail_templated import send_mail
from quotes.models import QuoteRequest, Project
from property.models import AssignedAccount
from django.contrib.auth.mixins import LoginRequiredMixin

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
            quotes = QuoteRequest.objects.filter(user=request.user)
            projects = Project.objects.filter(quote_request__user=request.user)
            context = {
                "quotes": quotes,
                "projects": projects,
                "quote_count": quotes.count(),
                "projects_count": projects.count()
            }
            return render(request, "user/home.html", context)
        elif request.user.user_type == "CO":
            return redirect("profile:contractor_profile")
        elif request.user.user_type == "AG":
            accounts = AssignedAccount.objects.filter(assigned_to=request.user).order_by('-id').select_related(
                "assigned_by", "assigned_to", "assigned_by__user_profile")
            context = {
                "accounts": accounts,
            }
            return render(request, "user/agent_home.html", context)
        else:
            return redirect("admins:dashboard")
    
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

    def get(self, request):
        agents = User.objects.filter(user_type='AG')
        context = {
            'agents': agents,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        agent_id = request.POST.get('agent')
        try:
            agent = User.objects.get(id=agent_id, user_type = 'AG')
            AssignedAccount.objects.get_or_create(
                assigned_to=agent,
                assigned_by=request.user,
                is_approved=True
            )
            if not agent.user_type in ['HO', 'AG']:
                messages.error(request, 'Only Home Owners can assign properties')
                return redirect('main:assign-agent')

            send_mail(
                'mail/assign_agent.tpl',
                {'first_name': agent.first_name, "base_url": get_base_url(request)},
                settings.EMAIL_HOST_USER,
                [agent.email]
            )

            messages.success(request, 'Agent assigned successfully. Awaiting agent confirmation')

        except Exception as e:
            print(e)
            messages.error(request, 'An error occured')

        return redirect('main:home')



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


