
from django.shortcuts import render, redirect, get_object_or_404
from profiles.models import ContractorProfile, UserProfile, AgentProfile
from django.urls import reverse
from django.contrib import messages
from django.db.models import Q

from profiles.services.contractor import ContractorService
from .forms import ContractorProfileForm, HomeOwnersEditForm, AgentEditForm, ProfilePictureForm
from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import get_user_model
from django.http import JsonResponse


User = get_user_model()

@login_required
def contractor_profile_view(request):
    print('poo')
    if request.user.user_type != 'CO':
        return redirect('main:home')
    
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
    else:
        # profile = ContractorProfile.objects.get(user=request.user)
        # form = ProfilePictureForm(instance = profile)
        try:
            profile = ContractorProfile.objects.get(user=request.user)
            form = ProfilePictureForm(instance = profile)
            context = {
                'profile' : profile,
                "form": form
            }
        except:
            print('failed')
            context = {}
            # return redirect('account_signup')
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
        contractorProfile = get_object_or_404(ContractorProfile, user=user.id)
        form = ContractorProfileForm(instance = contractorProfile, initial={'email' : user.email, 'phone_number' : user.phone_number})
        return render(request, 'user/editprofiles/contractor_edit_profile.html', {"details":contractorProfile,'form' :form})
    
    elif request.user.user_type == 'AG':
        agent_profile = get_object_or_404(AgentProfile, user=user.id)
        form = AgentEditForm(instance = agent_profile, initial={'email' : user.email, 'phone_number' : user.phone_number})
        return render(request, 'user/editprofiles/agents_edit_profile.html', {'form' :form})
    
    elif request.user.user_type == 'HO':
        user_profile = get_object_or_404(UserProfile, user=user.id)
        form = HomeOwnersEditForm(instance = user_profile, initial={'email' : user.email, 'phone_number' : user.phone_number})
        return render(request, 'user/editprofiles/home_owners_edit_profile.html', {"details":user_profile, 'form' :form})
    else:
        return redirect('main:dashboard')


@login_required
def editHomeOwnerProfileRequest(request):
    user = User.objects.get(id=request.user.id)
    print(user, "home user")
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
    contractor_profile = ContractorProfile.objects.get(user=user)
    print(request.FILES)
    print(request.POST)
    if request.method == 'POST':
        profile_form = ContractorProfileForm(request.POST, request.FILES, instance=contractor_profile)
        if profile_form.is_valid():
            # Save the form to update other profile fields
            profile_form.save()

            # Update profile picture if provided
            if 'image' in request.POST:
                contractor_profile.image = request.POST['image']
                contractor_profile.save()  # Save the contractor profile after updating the image

            # Update user details
            user.phone_number = profile_form.cleaned_data['phone_number']
            user.email = profile_form.cleaned_data['email']
            user.save()

            messages.success(request, 'Profile updated successfully!')
            return redirect('profile:contractor_profile')
        else:
            print(profile_form.errors)
            return render(request, 'user/editprofiles/contractor_edit_profile.html', {'form': profile_form})
    
    profile_form = ContractorProfileForm(instance=contractor_profile)
    return render(request, 'user/editprofiles/contractor_edit_profile.html', {'form': profile_form})

    


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
    if not query or not results:
        context['no_results'] = True
    return render(request, 'user/search_results.html', context)

@login_required
def upload_image(request):
    print(request.FILES)
    return redirect('profile:contractor_profile')


# def change_profile_pics_view(request):
#     if request.method == 'POST':
#         form = ProfilePictureForm(request.POST, request.FILES)
#         if form.is_valid():
#             # Get the uploaded image
#             image_instance = form.cleaned_data['image']
            
#             # Constructing a new filename
#             new_filename = f"{request.user.username}_profilepic_{request.user.id}.jpg"
            
#             # Check if a media instance with the new filename exists
#             existing_media_instance = Media.objects.filter(image__icontains=new_filename).first()
            
#             if existing_media_instance:
#                 # If an instance with the new filename exists, update its image
#                 existing_media_instance.image = image_instance
#                 existing_media_instance.upload_date = timezone.now()
#                 existing_media_instance.save()
#             else:
#                 # If no instance with the new filename exists, create a new one
#                 media_instance = Media.objects.create(
#                     content_object=request.user.contractor_profile,
#                     image=image_instance,
#                     upload_date=timezone.now()
#                 )
            
#             # Redirect to the user's profile page
#             return redirect('profile')
#     else:
#         form = ProfilePictureForm()
#     return render(request, 'change_profile_picture.html', {'form': form})


def change_profile_pics_view(request):
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES)
        if form.is_valid():
            image_instance = form.cleaned_data['image']
            
            # Get or create the ContractorProfile instance for the current user
            contractor_profile = ContractorProfile.objects.get(user=request.user)
            
            # Update the image field of the ContractorProfile instance
            contractor_profile.image = image_instance
            contractor_profile.save()
            
            # Redirect to the user's profile page
            return redirect('profile:contractor_profile')
        else:
            # print(form.errors)
            pass
    else:
        form = ProfilePictureForm()
    return render(request, 'user/contractor_home.html', {'form': form})

def show_agent_menu_view(request):
    return render(request, 'user/agent_menu.html', {})

def show_agent_message_view(request):
    return render(request, 'user/agent_message.html', {})

def update_onboarding_status(request):
    if request.method == 'POST':
        pass
        # Get the current user's AgentProfile instance
        # agent_profile = request.user.agent_profile
        # agent_profile.has_seen_onboarding_message = True
        # agent_profile.save()      
        # return JsonResponse({'message': 'Onboarding status updated successfully'}, status=200)
    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)
