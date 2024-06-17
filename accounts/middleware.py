# middlewares.py
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
from urllib.parse import urlparse, parse_qs


class GoogleOAuthCallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == '/accounts/google/login/callback/' and request.user.is_authenticated:
            if not request.session.get('user_type_selected'):
                sociallogin = SocialLogin.stash_state(request)
                request.session['sociallogin'] = sociallogin.serialize()
                return redirect('select_user_type')
        response = self.get_response(request)
        return response

            

