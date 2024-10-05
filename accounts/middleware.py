from django.shortcuts import redirect
from django.urls import reverse

class GoogleOAuthCallbackMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(request.path)
        if request.path == '/accounts/google/login/callback/' and request.user.is_authenticated:
            print('hy')
            if not request.session.get('user_type_selected'):
                return redirect(reverse('select_user_type'))

        response = self.get_response(request)
        return response
