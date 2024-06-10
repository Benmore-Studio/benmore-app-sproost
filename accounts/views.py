from django.shortcuts import render
from allauth.account.views import LoginView
from allauth.account.views import SignupView
from django.contrib.auth import get_user_model
from phonenumbers import parse, is_valid_number
from .forms import ValidatePhoneNumberForm, CustomSignupForm
from django.http import JsonResponse

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.template import loader


class CustomLoginView(LoginView):
    def form_valid(self, form):
        
        remember = self.request.POST.get('remember', None)
        if remember:
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        else:
            self.request.session.set_expiry(0)  # Browser close
        return super().form_valid(form)
    


class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    def dispatch(self, request, *args, **kwargs):
        print('****')
        return super().post(request, *args, **kwargs)


def validate_phone_numbers(request):
    phone_number = request.GET.get('phone')
    location = request.GET.get('location')
    form = ValidatePhoneNumberForm({'phone_number_1': phone_number, 'phone_number_0': location})
    if form.is_valid():
        return JsonResponse({'valid': form.is_valid()}, status=200)
    else:
        return JsonResponse({'valid': False, 'message' : 'Invalid phone number', 'errors': form.errors}, status=400)


def logout_user(request):
    logout(request)
    return redirect('account_login')



def custom_bad_request(request, exception):
    template = loader.get_template('400.html')
    return HttpResponseBadRequest(template.render({}, request))

def custom_server_error(request):
    template = loader.get_template('500.html')
    return HttpResponseServerError(template.render({}, request))
