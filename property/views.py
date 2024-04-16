from django.shortcuts import render, redirect
from quotes.models import Project, QuoteRequest
from django.contrib.auth import get_user_model
from django.contrib import messages

User = get_user_model()

def agents_home_owner_account(request, pk):
    try:
        home_owner = User.objects.get(pk=pk)
        quotes = QuoteRequest.objects.filter(user=home_owner)
        projects = Project.objects.filter(quote_request__user=home_owner)
        context = {
            "quotes": quotes,
            "projects": projects,
            "quote_count": quotes.count(),
            "projects_count": projects.count()
        }
        return render(request, 'user/home.html', context)
    except User.DoesNotExist:
        messages.error(request, 'Home Owner not found')
        return redirect('main:home')
        
        
    