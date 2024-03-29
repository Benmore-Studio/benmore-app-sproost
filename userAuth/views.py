from django.shortcuts import render
from allauth.account.views import LoginView
from django.contrib.auth import get_user_model

class CustomLoginView(LoginView):
    def form_valid(self, form):
        remember = self.request.POST.get('remember', None)
        if remember:
            print("setting session expiry to 30 days")
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        else:
            self.request.session.set_expiry(0)  # Browser close
        return super().form_valid(form)