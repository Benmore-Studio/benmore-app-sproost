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

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CustomSignupSerializer, GoogleSignUpSerializer
from rest_framework.generics import CreateAPIView




from allauth.socialaccount.models import SocialLogin
# from allauth.socialaccount.helpers import complete_social_signup
# from .utils import retrieve_sociallogin

from django.core.cache import cache
import uuid

from profiles.models import UserProfile, AgentProfile, ContractorProfile

from django.contrib.sites.shortcuts import get_current_site
import json
import requests







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
                # return complete_social_signup(request, sociallogin)
            else:
                return redirect('account_signup')
        else:
            logger.error('Form is not valid')
            logger.error(form.errors)
    else:
        form = UserTypeForm()
    return render(request, 'account/user_type_selection.html', {'form': form})


# class CustomSignupView(SignupView):
#     form_class = CustomSignupForm

#     def form_invalid(self, form):
#         # This method is called when the form is invalid
#         errors = form.errors
#         for field, error in errors.items():
#             pass
#             # print(f"Error in {field}: {error}")
#         return self.render_to_response(self.get_context_data(form=form))
    
#     def form_valid(self, form):
#         # If you want to print out the values being submitted
#         cleaned_data = form.cleaned_data
#         for field, value in cleaned_data.items():
#             pass
#             # print(f"{field}: {value}")
#         return super().form_valid(form)

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['is_staff'] = user.is_staff
        # token['is_superuser'] = user.is_superuser
        #         # ...

        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class ManualSignupView(CreateAPIView):
    serializer_class = CustomSignupSerializer

def authenticate_google_token(token):
    """
    Verifies the Google OAuth2 token and returns user information.
    :param token: The Google OAuth2 token received from the client
    :return: A dictionary with user information (email, first name, last name) if the token is valid,
             otherwise returns None.
    """
    # Google token verification URL
    google_token_info_url = "https://oauth2.googleapis.com/tokeninfo"

    # Send a GET request to Google's token verification endpoint
    response = requests.get(google_token_info_url, params={'id_token': token})

    # If the response is valid and the token is verified
    if response.status_code == 200:
        token_info = response.json()
        print(token_info)

        # Example token payload structure:
        # {
        #   "iss": "https://accounts.google.com",
        #   "sub": "110169484474386276334",
        #   "azp": "1234567890-abc.apps.googleusercontent.com",
        #   "aud": "1234567890-abc.apps.googleusercontent.com",
        #   "iat": "1496117114",
        #   "exp": "1496120714",
        #   "email": "email@example.com",
        #   "email_verified": "true",
        #   "name": "Full Name",
        #   "picture": "https://lh5.googleusercontent.com/photo.jpg",
        #   "given_name": "First",
        #   "family_name": "Last",
        # }

        # Ensure the token was issued by Google and email is verified
        if token_info['iss'] == "https://accounts.google.com" and token_info.get('email_verified') == "true":
            # Extract user information from the token
            user_info = {
                'email': token_info['email'],
                'first_name': token_info.get('given_name'),
                'last_name': token_info.get('family_name'),
            }
            return user_info  # Return user information

    # If the token is invalid or not verified, return None
    return None

# class GoogleSignUp(APIView):
#     """
#     View to receive Google OAuth2 tokens, create new user accounts, or link to existing ones.
#     """
#     def post(self, request):
#         # Retrieve the Google OAuth2 token from the request
#         serializer = GoogleSignUpSerializer(data=request.data)
#         if serializer.is_valid():
#             token = request.data.get('token')
            
#             # Authenticate the Google token and get user information
#             user_info = authenticate_google_token(token)
            
#             if user_info:
#                 # Populate the serializer with the Google-provided data (assuming user_info is a dict)
#                 serializer = CustomSignupSerializer(data={
#                     'first_name': user_info.get('first_name'),
#                     'last_name': user_info.get('last_name'),
#                     'email': user_info.get('email'),
#                     'password': user_info.get('password', 'defaultpassword'),  # Handle password securely
#                     'user_type': 'HO',  # or dynamically from user_info if available
#                     # Populate other required fields if applicable
#                 })

#                 # Validate and create the user account if valid
#                 if serializer.is_valid():
#                     serializer.save()
#                     return Response({'message': 'User created successfully', 'user': serializer.data}, status=status.HTTP_201_CREATED)
#                 else:
#                     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
#             # If the token is invalid, return an unauthorized response
#             return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)


class GoogleSignUp(generics.GenericAPIView):
    """
    View to receive Google OAuth2 tokens, create new user accounts, or link to existing ones.
    """
    serializer_class = GoogleSignUpSerializer

    def post(self, request):
        # Use the GoogleSignUpSerializer to validate the incoming data
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Retrieve the validated token from the serializer
            token = serializer.validated_data.get('token')
            
            # Authenticate the Google token and get user information
            user_info = authenticate_google_token(token)
            
            if user_info:
                # Populate the CustomSignupSerializer with the Google-provided data
                signup_serializer = CustomSignupSerializer(data={
                    'first_name': user_info.get('first_name'),
                    'last_name': user_info.get('last_name'),
                    'email': user_info.get('email'),
                    'password': 'defaultpassword',  # Handle password securely
                    'user_type': 'HO',  # Assign a default user type for example
                })

                if signup_serializer.is_valid():
                    signup_serializer.save()
                    return Response({'message': 'User created successfully', 'user': signup_serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response(signup_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # If the token is invalid, return validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        # print(f'Failed to send verification email to {email}: {e}')
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
        except json.JSONDecodeError as e:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)

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