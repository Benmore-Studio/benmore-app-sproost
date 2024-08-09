from django.shortcuts import render
from allauth.account.views import LoginView
from allauth.account.views import SignupView
from django.contrib.auth import get_user_model
from phonenumbers import parse, is_valid_number
from .forms import ValidatePhoneNumberForm, CustomSignupForm, UserTypeForm, EmailverificationForm
from django.http import JsonResponse

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.http import HttpResponseBadRequest, HttpResponseServerError
from django.template import loader
from django.template.loader import render_to_string
from django.http import HttpResponse
import random
from mail_templated import send_mail
from django.conf import settings

from datetime import timedelta




from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.helpers import complete_social_signup
# from .utils import retrieve_sociallogin

from django.core.cache import cache
import uuid

from profiles.models import UserProfile, AgentProfile, ContractorProfile

from django.contrib.sites.shortcuts import get_current_site
import json






import logging

logger = logging.getLogger(__name__)


User = get_user_model()


def get_base_url(request):
    # Use 'get_current_site' to get the domain
    domain = get_current_site(request).domain
    # Use 'request.is_secure' to determine the scheme (http or https)
    scheme = 'https' if request.is_secure() else 'http'
    # Construct the base URL
    base_url = f"{scheme}://{domain}"
    return base_url

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
    
    while User.objects.filter(username=username).exists():
        username = f"{base_username}{counter}"
        counter += 1
    return username


def select_user_type(request):
    if request.method == 'POST':
        form = UserTypeForm(request.POST)
        
        if form.is_valid():
            sociallogin_key = request.session.get('sociallogin_key')    
            user_type = form.cleaned_data['user_type']
            request.session['user_type'] = user_type
            request.session['user_type_selected'] = True
            sociallogin = retrieve_sociallogin(request)
            
            if sociallogin:
                username = generate_username(sociallogin.user.email)
                sociallogin.user.username = username 
                sociallogin.user.user_type = user_type  # Set user type before completing signup
                sociallogin.user.save()
                if sociallogin.user.user_type == "HO":
                    UserProfile.objects.create(user = sociallogin.user) 
                elif sociallogin.user.user_type == "AG":
                    AgentProfile.objects.create(user = sociallogin.user)                
                elif sociallogin.user.user_type == "CO":
                    ContractorProfile.objects.create(user = sociallogin.user)                
                return complete_social_signup(request, sociallogin)
            else:
                return redirect('account_signup')
        else:
            logger.error('Form is not valid')
            logger.error(form.errors)
    else:
        form = UserTypeForm()
    return render(request, 'account/user_type_selection.html', {'form': form})


class CustomSignupView(SignupView):
    form_class = CustomSignupForm

    def form_invalid(self, form):
        # This method is called when the form is invalid
        errors = form.errors
        for field, error in errors.items():
            print(f"Error in {field}: {error}")
        return self.render_to_response(self.get_context_data(form=form))
    
    def form_valid(self, form):
        # If you want to print out the values being submitted
        cleaned_data = form.cleaned_data
        for field, value in cleaned_data.items():
            print(f"{field}: {value}")
        return super().form_valid(form)



def generate_verification_code():
    return f"{random.randint(100000, 999999)}"


def send_verification_email(request, user, verification_code, email):

    try:       
        send_mail(
            'mail/email_send.tpl',
            {'first_name': user.first_name,'verification_code': verification_code,"base_url": get_base_url(request)},
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently=False,
        )
    
    except Exception as e:
        print(f'Failed to send verification email to {email}: {e}')
        return HttpResponse("An error occurred while sending the email.", status=500)

    return HttpResponse("Verification email sent.", status=200)


def verify_email(request):
    verification_code = generate_verification_code()
    request.session['verification_code']=verification_code
    request.session.set_expiry(timedelta(minutes=30 ))

    return render(request, 'account/verify_email.html', {})


def verify_email_two(request):
    if request.user.is_authenticated:
        stored_code = request.session.get('verification_code')
        user = request.user
        try:
            data = json.loads(request.body)
            print(f"Debug: Raw request body data = {request.body}")
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

        print('data')
        if User.objects.filter(email=data['email']).exclude(id=user.id).exists():
            return JsonResponse({'status': 'error','message': 'Email already exists for other users'}, status=400)
        else:
            email_result = send_verification_email(request, user, stored_code, data['email'])
            if email_result.status_code == 200:
                request.session['email_data']=data
                return JsonResponse({'status': 'success', 'message': 'Email sent', 'stored_code':stored_code}, status=200)
            return JsonResponse({'message': 'Email not found'}, status=400)

    else:
        return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=401)


def final_email_verification(request):
    stored_email = request.session.get('email_data')
    user = request.user

    form = EmailverificationForm(stored_email, instance=user)
    if form.is_valid():
        email = form.cleaned_data['email']
        user.email = email
        user.save()
        return redirect('main:home')
    else:
        return render(request, 'account/verify_email.html', {})




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