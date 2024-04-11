from django.shortcuts import render, redirect
from profiles.models import ContractorProfile
from django.shortcuts import get_object_or_404
# from django.contrib import messages
from django.db.models import Q
from .forms import ContractorProfileForm

def contractor_profile_view(request):
    return render(request, 'user/contractor_home.html', {'loggedInUser' : 'contractor'})


def editProfile(request):
    context ={}
    return render(request, 'user/edit_profile.html', context)

# views.py
def editProfileRequest(request):
    user = request.user
    try:
        contractor_profile = ContractorProfile.objects.get(user=user.id)
    
        if request.method == 'POST':
            profile_form = ContractorProfileForm(request.POST, instance=contractor_profile)
            if profile_form.is_valid():
                profile_form.save()

                user.phone_number = profile_form.cleaned_data['phone_number']
                user.email = profile_form.cleaned_data['email']
                user.save()
                return redirect('profile:contractor_profile')
            else:
                print(profile_form.errors)
        else:
            profile_form = ContractorProfileForm(instance=contractor_profile)
    except ContractorProfile.DoesNotExist:
        # Redirect to profile creation page if profile doesn't exist
        return redirect('profile:edit-profile')

    print("hooy")
    return render(request, 'user/edit_profile.html', {'profile_form': profile_form})


def search_view(request):
    context ={}
    return render(request, 'user/search_results.html', context)

def search_view_results(request):
    if request.method == 'GET':
        query = request.GET.get('search')
        results = []

        if query:
            # Perform search based on Title, Speciality, Email, and Phone number
            results = ContractorProfile.objects.filter(
                Q(user__username__icontains=query) |
                Q(specialization__icontains=query) |
                Q(user__phone_number__icontains=query)|
                Q(user__email__icontains=query) 
            )
            num_results = len(results)   
                
        return render(request, 'user/search_results.html', {'results': results, 'num_results': num_results})

