# custom_adapter.py
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if request.user.user_type == 'HO':
            return reverse("main:dashboard")
        elif request.user.user_type == 'CO':
            return reverse("profile:contractor_profile")
        
        return super().get_login_redirect_url(request)