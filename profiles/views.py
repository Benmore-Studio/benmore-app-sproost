from django.shortcuts import render


def contractor_profile_view(request):
    return render(request, 'user/contractor_home.html', {'loggedInUser' : 'contractor'})
