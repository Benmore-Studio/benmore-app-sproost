from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Case, When, CharField
from quotes.models import Project, QuoteRequest
from property.models import AssignedAccount
from django.db.models import Prefetch
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse

User = get_user_model()

@login_required
def adminDashboard(request):
    counts = User.objects.aggregate(
        home_owner_count=Count(Case(When(user_type='HO', then=1), output_field=CharField())),
        agent_count=Count(Case(When(user_type='AG', then=1), output_field=CharField())),
        contractor_count=Count(Case(When(user_type='CO', then=1), output_field=CharField())),
    )
    active_projects = Project.objects.filter(is_approved=True).count()
    
    
    recent_home_owners = User.objects.filter(user_type='HO').prefetch_related('quote_requests').order_by('-id')[:4]
    recent_agents = User.objects.filter(user_type='AG').annotate(
            total_projects=Count('assigned_properties_to__assigned_by__quote_requests__quote_project'),
    ).order_by('-id')[:4]
    recent_quote_requests = QuoteRequest.objects.select_related("user").order_by('-id')[:4]
    recent_contractors = User.objects.filter(user_type='CO').select_related("contractor_profile").order_by('-id')[:4]
    
    overall_stats = [
        {'title':'Home Owners', 'project_counts': counts['home_owner_count'], 'increased_by':'20%', 'action':'View owners', 'link' : reverse('admins:homeowners')},
        {'title':'Agents', 'project_counts': counts['agent_count'], 'increased_by':'10%', 'action':'View agents', 'link' : reverse('admins:agents')},
        {'title':'Contractors', 'project_counts': counts['contractor_count'], 'increased_by':'10%', 'action':'View contractors', 'link' : reverse('admins:contractors')},
        {'title':'Active Projects', 'project_counts': active_projects, 'increased_by':'40%', 'action':'View projects',},
    ]
    context ={'recent_home_owners': recent_home_owners, 'recent_agents':recent_agents,
              'recent_contractors': recent_contractors, 'recent_quote_requests': recent_quote_requests, 'overall_stats': overall_stats }  
    return render(request, 'user_admin/dashboard.html', context)

def contractorsListView(request):
    query = request.GET.get('q')
    contractors = User.objects.filter(user_type='CO').select_related("contractor_profile").order_by('-id')
    if query:
        #search by company_name, email, address
        contractors = contractors.filter(
            Q(contractor_profile__company_name__icontains=query) |
            Q(email__icontains=query) 
        )
    
    # Pagination
    paginator = Paginator(contractors, 10)  # Show 10 orders per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'contractors': page_obj}
    return render(request, 'user_admin/contractors.html', context)

def homeOwnersListView(request):
    query = request.GET.get('q')
    home_owners = User.objects.filter(user_type='HO').select_related("user_profile").prefetch_related('quote_requests').order_by('-id')
    if query:
        home_owners = home_owners.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(user_profile__city__icontains=query) |
            Q(user_profile__state_province__icontains=query) |
            Q(email__icontains=query) 
        )
    # Pagination
    paginator = Paginator(home_owners, 10)  # Show 10 orders per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {'homeowners': page_obj}
    return render(request, 'user_admin/home_owners.html', context)

def agentsListView(request):
    query = request.GET.get('q')
    agents = User.objects.filter(user_type='AG').select_related("user_profile").annotate(
            total_projects=Count('assigned_properties_to__assigned_by__quote_requests__quote_project'),
    ).order_by('-id')
    
    if query:
        agents = agents.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(user_profile__city__icontains=query) |
            Q(user_profile__state_province__icontains=query) |
            Q(email__icontains=query) 
        )
    # Pagination
    paginator = Paginator(agents, 10)  # Show 10 orders per page.
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {'agents': page_obj}
    return render(request, 'user_admin/agents.html', context)

