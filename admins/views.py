from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Case, When, CharField
from django.db.models import Q
from django.core.paginator import Paginator
from django.urls import reverse
from quotes.models import Project, QuoteRequest, QuoteRequestStatus
from .forms import UpdateAgentForm, UpdateContractorProfileForm, QuoteStatusForm, UpdateHomeOwnerForm
from django.http import HttpResponseBadRequest, HttpResponseNotFound
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from profiles.models import AgentProfile, ContractorProfile, UserProfile
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages


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
        {'title':'Home Owners', 'project_counts': counts['home_owner_count'], 'action':'View owners', 'link' : reverse('admins:homeowners')},
        {'title':'Agents', 'project_counts': counts['agent_count'], 'action':'View agents', 'link' : reverse('admins:agents')},
        {'title':'Contractors', 'project_counts': counts['contractor_count'], 'action':'View contractors', 'link' : reverse('admins:contractors')},
        {'title':'Active Projects', 'project_counts': active_projects, 'action':'View projects', 'link' : reverse('admins:active-projects')},
    ]
    context ={'recent_home_owners': recent_home_owners, 'recent_agents':recent_agents,
              'recent_contractors': recent_contractors, 'recent_quote_requests': recent_quote_requests, 'overall_stats': overall_stats,
              }  
    return render(request, 'user_admin/dashboard.html', context)

@login_required
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

@login_required
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


@login_required
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

@login_required
def projectRequest(request):
    project_history = QuoteRequest.objects.all()
    query = request.GET.get('q')
    if query:
        project_history = project_history.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(title__icontains=query) 
        )
        
    paginator = Paginator(project_history, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'project_history': project_history,
        'page_obj': page_obj,
    }
    return render(request, 'user_admin/project_request.html', context)

@login_required
def projectRequestDetail(request, id):
    quote_request = QuoteRequest.objects.get(id=id)

    if request.method == "POST":
        decision = request.POST.get('decision')
        if decision == "accept":
            pdf = request.FILES['pdf']
            Project.objects.get_or_create(
                admin=request.user,
                quote_request=quote_request,
                file=pdf,
                is_approved=True
            )
            quote_request.status = QuoteRequestStatus.approved
            quote_request.save(update_fields=['status'])

        else:
            quote_request.status = QuoteRequestStatus.rejected
            quote_request.save(update_fields=['status'])
            
    quotation_items = [
        {'name': 'Building Material', 'price': '20,000'},
        {'name': 'Rentals', 'price': '5000'},
        {'name': 'Cleaning', 'price': '8000'},
        {'name': 'Cleaning', 'price': '8000'},
        {'name': 'Labour', 'price': '10,000'},
    ]
    quotation_history = [
        {'date': 'Jan 16, 2024', 'contractor_name': 'Olivia Rhye', 'price': '$43,000', 'status': 'pending'},
        {'date': 'Jan 16, 2024', 'contractor_name': 'Olivia Rhye', 'price': '$43,000', 'status': 'pending'},
        {'date': 'Jan 16, 2024', 'contractor_name': 'Olivia Rhye', 'price': '$43,000', 'status': 'pending'},
    ]
    quotation_history_length = len(quotation_history)
    # Quotation history length greater than 0 will change the UI under quotations history, defaulted to 0 at the beginning
    context = {'quotation_items': quotation_items, 'quotation_history_length': 0,
               'quotation_history': quotation_history, 'quote': quote_request}
    return render(request, 'user_admin/project_request_detail.html', context)

@login_required
def activeProjectList(request):
    active_projects = Project.objects.filter(is_approved=True).select_related('quote_request').order_by('-id')
    query = request.GET.get('q')
    if query:
        active_projects = active_projects.filter(
            Q(quote_request__user__first_name__icontains=query) |
            Q(quote_request__user__last_name__icontains=query) |
            Q(quote_request__title__icontains=query) 
        )
    paginator = Paginator(active_projects, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'projects': page_obj
    }
    return render(request, 'user_admin/active_projects.html', context)

def changeQuoteStatus(request, pk):
    try:
        quote = QuoteRequest.objects.get(pk = pk)
        form = QuoteStatusForm(request.POST or None)
        if form.is_valid():
            status = form.cleaned_data.get('status')
            if str(status).lower() == "approved":
                Project.objects.get_or_create(
                    admin=request.user,
                    quote_request=quote,
                    is_approved=True
                )
            else :
                project = Project.objects.filter(quote_request=quote, is_approved=True).first()
                if project:
                    project.delete()
                    
            quote.status = status
            quote.save()
        else:
            return HttpResponseBadRequest("wrong input")
    
    except QuoteRequest.DoesNotExist:
        return HttpResponseNotFound("Quote not found")
    
    return render(request, 'user_admin/partials/QuoteStatusForm.html', {'quote' : quote})


class updateContractor(LoginRequiredMixin, View):
    form_class = UpdateContractorProfileForm
    template_name = 'user_admin/update_contractor.html'
    success_url = reverse_lazy('admins:contractors')
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get('pk'))
        obj = ContractorProfile.objects.get_or_create(user=user)[0]
        form = self.form_class(instance=obj, initial = { 'email' : user.email , 'phone_number' : user.phone_number})
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        try:
            obj = ContractorProfile.objects.get(user__id=self.kwargs.get('pk'))
            form = self.form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                obj.user.email = form.cleaned_data.get('email')
                obj.user.phone_number = form.cleaned_data.get('phone_number')
                obj.user.save()
                messages.success(self.request, 'Contractor updated successfully')
                return redirect(self.success_url)
            return render(request, self.template_name, {'form': form})
        except ContractorProfile.DoesNotExist:
            messages.error(self.request, 'An Error Occurred, Contractor not found')
            return redirect(self.success_url)
        
class updateHomeOwner(LoginRequiredMixin, View):
    form_class = UpdateHomeOwnerForm
    template_name = 'user_admin/update_home_owner.html'
    success_url = reverse_lazy('admins:homeowners')
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get('pk'))
        obj = UserProfile.objects.get_or_create(user=user)[0]
        form = self.form_class(instance=obj, initial = { 'email' : user.email , 'phone_number' : user.phone_number})
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        try:
            obj = UserProfile.objects.get(user__id=self.kwargs.get('pk'))
            form = self.form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                obj.user.email = form.cleaned_data.get('email')
                obj.user.phone_number = form.cleaned_data.get('phone_number')
                obj.user.save()
                messages.success(self.request, 'Home Owner updated successfully')
                return redirect(self.success_url)
            return render(request, self.template_name, {'form': form})
        except ContractorProfile.DoesNotExist:
            messages.error(self.request, 'An Error Occurred, Home Owner not found')
            return redirect(self.success_url)
        
class UpdateAgent(LoginRequiredMixin, View):
    form_class = UpdateAgentForm
    template_name = 'user_admin/update_agent.html'
    success_url = reverse_lazy('admins:agents')
    
    def get(self, request, *args, **kwargs):
        user = User.objects.get(id=self.kwargs.get('pk'))
        print(user)
        obj = AgentProfile.objects.get_or_create(user=user)[0]
        form = self.form_class(instance=obj, initial = { 'email' : user.email , 'phone_number' : user.phone_number})
        return render(request, self.template_name, {'form': form})
    
    def post(self, request, *args, **kwargs):
        try:
            obj = AgentProfile.objects.get(user__id=self.kwargs.get('pk'))
            form = self.form_class(request.POST, instance=obj)
            if form.is_valid():
                form.save()
                obj.user.email = form.cleaned_data.get('email')
                obj.user.phone_number = form.cleaned_data.get('phone_number')
                obj.user.save()
                messages.success(self.request, 'Agent updated successfully')
                return redirect(self.success_url)
            return render(request, self.template_name, {'form': form})
        except ContractorProfile.DoesNotExist:
            messages.error(self.request, 'An Error Occurred, Agent not found')
            return redirect(self.success_url)

    
