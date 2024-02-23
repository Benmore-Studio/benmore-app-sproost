from django.shortcuts import render

# Create your views here.
def home(request):
    context = {}
    return render(request, 'user/home-owner.html', context)

def loginUser(request):
    context = {}
    return render(request, 'user/auth/login.html', context)

def signUpUser(request):
    context = {}
    return render(request, 'user/auth/signup.html', context)