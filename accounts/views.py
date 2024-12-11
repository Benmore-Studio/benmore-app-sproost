from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt



from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.generics import CreateAPIView

from .serializers import CustomSignupSerializer, GoogleSignUpSerializer

from drf_spectacular.utils import extend_schema, OpenApiResponse

import random
from .models import OTP
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
from rest_framework.generics import GenericAPIView
from .serializers import SendOTPSerializer, VerifyOTPSerializer

import random


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
    '''
    substitute Real_estate_license with registration_ID in the data you send,    
    substitute brokerage_address with agent_address in the data you send for agents
    '''
    serializer_class = CustomSignupSerializer
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)



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


class GoogleTokenAuthenticateView(APIView):
    """
    Authenticates the Google OAuth2 token and returns user details.
    """
    serializer_class = GoogleSignUpSerializer
    def post(self, request):
        # Extract the token from the request data
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Authenticate the Google token
        user_info = authenticate_google_token(token)
        if user_info:
            return Response(
                {'message': 'Token authenticated successfully', 'user_info': user_info},
                status=status.HTTP_200_OK
            )
        else:
            return Response({'error': 'Invalid or expired token'}, status=status.HTTP_401_UNAUTHORIZED)


class CompleteSignupView(GenericAPIView):
    """
    Completes the user registration after receiving all user details from the frontend.
    """
    serializer_class = CustomSignupSerializer

    def post(self, request):
        # Validate and process the data using the CustomSignupSerializer
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'User created successfully', 'user': serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @method_decorator(csrf_exempt, name='dispatch') 
class LogoutView(APIView):
    """
    Handles logout by blacklisting the refresh token.
    """

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'refresh_token': {
                        'type': 'string',
                        'description': 'The refresh token to be blacklisted',
                    },
                },
                'required': ['refresh_token'],
            },
        },
        responses={
            205: OpenApiResponse(description="Successfully logged out"),
            400: OpenApiResponse(description="Bad request (e.g., invalid refresh token)"),
        }
    )


    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)



class SendOTPView(GenericAPIView):
    """
    Generates and sends OTP to the user's email.
    """
    serializer_class = SendOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.filter(email=email).first()

        if user:
            return Response({"error": "User with this email already exist."}, status=status.HTTP_409_CONFLICT)
        else:
            # Generate OTP
            try:
                otp = OTP.objects.get(email=email)
                otp.delete()
            except:
                pass
            otp_code = f"{random.randint(100000, 999999)}"

            OTP.objects.create(
                email = email,
                otp_code=otp_code,
                expires_at=now() + timedelta(minutes=10)  # OTP expires in 10 minutes
            )

            # Send OTP via email
            try:
                send_mail(
                    subject="Your OTP Code",
                    message=f"Your OTP code is: {otp_code}. It expires in 10 minutes.",
                    from_email= 'no-reply@yourdomain.com',
                    recipient_list=[email],
                )
            except BadHeaderError:
                return Response({'error': 'Invalid header found.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f"Error sending email: {e}"}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"message": f"OTP sent to your email. otp_code-{otp_code}"}, status=status.HTTP_200_OK)


class VerifyOTPView(GenericAPIView):
    """
    Verifies the OTP sent to the user's email.
    """
    serializer_class = VerifyOTPSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']

        # # Find the user
        # user = User.objects.filter(email=email).first()
        # if not user:
        #     return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if a valid OTP exists
        otp = OTP.objects.filter(email=email, otp_code=otp_code).first()
        if not otp:
            return Response({"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the OTP is expired
        if not otp.is_valid():
            return Response({"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST)

        # OTP is valid
        otp.delete()  # Delete the OTP after successful verification
        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)

# def validate_phone_numbers(request):
#     phone_number = request.GET.get('phone')
#     location = request.GET.get('location')
#     form = ValidatePhoneNumberForm({'phone_number_1': phone_number, 'phone_number_0': location})
#     if form.is_valid():
#         return JsonResponse({'valid': form.is_valid()}, status=200)
#     else:
#         return JsonResponse({'valid': False, 'message' : 'Invalid phone number', 'errors': form.errors}, status=400)



# def custom_bad_request(request, exception):
#     template = loader.get_template('400.html')
#     return HttpResponseBadRequest(template.render({}, request))

# def custom_server_error(request):
#     template = loader.get_template('500.html')
#     return HttpResponseServerError(template.render({}, request))


