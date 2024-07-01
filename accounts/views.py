from django.shortcuts import render
from allauth.account.views import LoginView
from allauth.account.views import SignupView
from django.contrib.auth import get_user_model
from phonenumbers import parse, is_valid_number
from .forms import ValidatePhoneNumberForm, CustomSignupForm, UserTypeForm
from django.http import JsonResponse

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.template import loader


from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.helpers import complete_social_signup
# from .utils import retrieve_sociallogin

from django.core.cache import cache
import uuid

from profiles.models import UserProfile, AgentProfile, ContractorProfile




import logging

logger = logging.getLogger(__name__)




class CustomLoginView(LoginView):
    def form_valid(self, form):
        
        remember = self.request.POST.get('remember', None)
        if remember:
            self.request.session.set_expiry(30 * 24 * 60 * 60)  # 30 days
        else:
            self.request.session.set_expiry(0)  # Browser close
        return super().form_valid(form)

def handle_google_callback(request):
    if request.user.is_authenticated:
        # Social login data should already be available here
        sociallogin = SocialLogin.from_request(request)
        if sociallogin:
            sociallogin_key = str(uuid.uuid4())
            cache.set(sociallogin_key, sociallogin.serialize(), timeout=600)  # Store for 10 minutes
            request.session['sociallogin_key'] = sociallogin_key
            return redirect('select_user_type')
    return redirect('account_login')

def retrieve_sociallogin(request):
    sociallogin_key = request.session.get('sociallogin_key')
    if sociallogin_key:
        sociallogin_data = cache.get(sociallogin_key)
        if sociallogin_data:
            return SocialLogin.deserialize(sociallogin_data)
    return None

def generate_username(email):
    base_username = email.split('@')[0]
    username = base_username
    counter = 1
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


def select_user_type(request):
    if request.method == 'POST':
        print('Received POST request')
        form = UserTypeForm(request.POST)
        print('Form initialized with POST data')
        print(form)
        
        if form.is_valid():
            print('Form is valid')
            sociallogin_key = request.session.get('sociallogin_key')
            print(request.session)
            print(cache.get(sociallogin_key))
            user_type = form.cleaned_data['user_type']
            print(f'Selected user type: {user_type}')
            request.session['user_type'] = user_type
            request.session['user_type_selected'] = True
            print('User type saved to session')

            sociallogin = retrieve_sociallogin(request)
            
            if sociallogin:
                print('Sociallogin data found in session')
                username = generate_username(sociallogin.user.email)
                sociallogin.user.username = username 
                sociallogin.user.user_type = user_type  # Set user type before completing signup
                sociallogin.user.save()
                if sociallogin.user.user_type == "HO":
                    UserProfile.objects.create(user = sociallogin.user) 
                    print('ho')
                elif sociallogin.user.user_type == "AG":
                    AgentProfile.objects.create(user = sociallogin.user) 
                print('ag')
                print(sociallogin.user)
                print('User type set and user saved')
                return complete_social_signup(request, sociallogin)
            else:
                print('No sociallogin data found in session, redirecting to login')
                return redirect('account_signup')
        else:
            print('Form is not valid')
            print(form.errors)
            logger.error('Form is not valid')
            logger.error(form.errors)
    else:
        form = UserTypeForm()
    return render(request, 'account/user_type_selection.html', {'form': form})


class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    def dispatch(self, request, *args, **kwargs):
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



# def user_type_selection(request):
#     if request.method == 'POST':
#         form = UserTypeForm(request.POST)
#         if form.is_valid():
#             request.session['user_type'] = form.cleaned_data['user_type']
#             print(f"User type set in session: {request.session['user_type']}")
#             sociallogin_data = request.session.pop('sociallogin', None)
#             print(f"Sociallogin data from session: {sociallogin_data}")

#             if sociallogin_data:
#                 sociallogin = SocialLogin.deserialize(sociallogin_data)
#                 return complete_social_login(request, sociallogin)  # Complete the social login process
#             else:
#                 return redirect('account_login')
#     else:
#         form = UserTypeForm()
#     return render(request, 'user_type_selection.html', {'form': form})