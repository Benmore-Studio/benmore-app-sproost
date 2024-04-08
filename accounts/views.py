from django.shortcuts import render
# authentication

# loggedInUser = 'home-owner'| 'agent'| 'contractor'| 'investor', this is used to switch between bottom navigation, default navigation is home-owner, so need to add it.

loggedInUser = 'home-owner'

# take a look at each template to know why this loggedInUser is used


def loginUser(request):
    context = {}
    return render(request, 'user/auth/login.html', context)

def signUpUser(request):
    context = {}
    return render(request, 'user/auth/signup.html', context)