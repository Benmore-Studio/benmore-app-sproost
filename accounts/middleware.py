from django.shortcuts import redirect
from .utils import stash_sociallogin
from allauth.socialaccount.models import SocialLogin

class GoogleOAuthCallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/google/login/callback/' and request.user.is_authenticated:
            # if not request.session.get('user_type_selected'):
            # sociallogin = SocialLogin.deserialize(request)
            # print('sociallogin')
            # print(sociallogin)
            # stash_sociallogin(request, sociallogin)
            return redirect('select_user_type')
        
        response = self.get_response(request)
        return response
