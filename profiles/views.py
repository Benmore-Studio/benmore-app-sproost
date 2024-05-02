
from django.shortcuts import render, redirect
from profiles.models import ContractorProfile, UserProfile, AgentProfile
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q

from profiles.services.contractor import ContractorService
from .forms import ContractorProfileForm, HomeOwnersEditForm, AgentEditForm
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def contractor_profile_view(request):
    if request.user.user_type != 'CO':
        return redirect('main:dashboard')
    
    if request.method == "POST":
        if request.FILES:
            media = request.FILES.getlist("upload-media")
            data = {
                "media": media
            }
            contractor_service = ContractorService(request=request)
            add_media, error = contractor_service.add_media(data)

            if error:
                messages.error(request, error)
            else:
                messages.success(request, add_media)
        else:
            messages.error(request, "No file found!")
        
        return redirect("profile:contractor_profile")
    
    
    # TODO add try and except to catch possible errors
    profile = ContractorProfile.objects.get(user = request.user)

    context = {
        'profile' : profile,
    }
    return render(request, 'user/contractor_home.html', context)

class contractorDetails(DetailView):
    """ for viewing contractor profile details"""
    model = ContractorProfile
    template_name = 'user/contractor_home.html'
    context_object_name = 'profile'

    def get_object(self):
        try:
            return ContractorProfile.objects.get(pk=self.kwargs['pk'])
        except ContractorProfile.DoesNotExist:
            # return to page user came from if profile doesn't exist
            print('Profile does not exist')
            return redirect('profile:contractor_profile')


# refactored this view so that only one view handles all the edit profile for differennt users
@login_required
def editProfile(request):
    user = request.user
    # render CO edit page if user type is CO
    if request.user.user_type == 'CO': 
        contractorProfile = ContractorProfile.objects.get(user = user.id)
        form = ContractorProfileForm(instance = contractorProfile, initial={'email' : user.email, 'phone_number' : user.phone_number})
        return render(request, 'user/editprofiles/contractor_edit_profile.html', {"details":contractorProfile,'form' :form})
    
    elif request.user.user_type == 'AG':
        agent_profile = AgentProfile.objects.get(user = user.id)
        form = AgentEditForm(instance = agent_profile, initial={'email' : user.email, 'phone_number' : user.phone_number})
        return render(request, 'user/editprofiles/agents_edit_profile.html', {'form' :form})
    
    elif request.user.user_type == 'HO':
        user_profile = UserProfile.objects.get(user = user.id)
        form = HomeOwnersEditForm(instance = user_profile, initial={'email' : user.email, 'phone_number' : user.phone_number})
        return render(request, 'user/editprofiles/home_owners_edit_profile.html', {"details":user_profile, 'form' :form})
    else:
        return redirect('main:dashboard')


@login_required
def editHomeOwnerProfileRequest(request):
    user = request.user
    user_profile = UserProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = HomeOwnersEditForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            user.phone_number = form.cleaned_data['phone_number']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('main:home')
        else:
            return render(request, 'user/editprofiles/home_owners_edit_profile.html', {'form': form})
    return redirect('profile:edit-profile')

@login_required
def editAgentProfile(request):
    user = request.user
    user_profile = AgentProfile.objects.get_or_create(user=request.user)[0]
    if request.method == 'POST':
        form = AgentEditForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            user.phone_number = form.cleaned_data['phone_number']
            user.email = form.cleaned_data['email']
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('main:home')
        else:
            return render(request, 'user/editprofiles/agents_edit_profile.html', {'form': form})
    return redirect('profile:edit-profile')


@login_required
def ContractorProfileEditView(request):
    user = request.user
    contractor_profile = ContractorProfile.objects.get_or_create(user=user)[0]

    if request.method == 'POST':
        profile_form = ContractorProfileForm(request.POST, instance=contractor_profile)
        if profile_form.is_valid():
            profile_form.save()

            user.phone_number = profile_form.cleaned_data['phone_number']
            user.email = profile_form.cleaned_data['email']
            user.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile:contractor_profile')
        else:
            return render(request, 'user/editprofiles/contractor_edit_profile.html', {'form': profile_form})
    
    return redirect('profile:contractor_profile')

    


@login_required
def search_view(request):
    query = request.GET.get('query')
    results = []
    if query:
        # Perform search based on Title, Speciality, Email, and Phone number
        results = ContractorProfile.objects.filter(
            Q(company_name__icontains=query) |
            Q(specialization__icontains=query) |
            Q(user__phone_number__icontains=query)|
            Q(user__email__icontains=query) 
        )   
    context = {'results': results}
    
    return render(request, 'user/search_results.html', context)

@login_required
def upload_image(request):
    print(request.FILES)
    return redirect('profile:contractor_profile')
