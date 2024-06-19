# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
import uuid


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        print(23)
        if request.user.user_type == '':
            print('lo')
            return reverse("select_user_type")
        # elif request.user.user_type == 'CO':
        #     return reverse("profile:contractor_profile")
        
        return super().get_login_redirect_url(request)

    # def pre_social_login(self, request, sociallogin: SocialLogin):
    #     print("pre_social_login called")
    #     print(sociallogin)
    #     user = sociallogin.user
    #     if not user.id:  # If user doesn't exist yet
    #         print('lop344')
    #         existing_user = self.get_existing_user(user)
    #         if existing_user:
    #             print(344)
    #             sociallogin.connect(request, existing_user)
    #             print(123)
    #         else:
    #             sociallogin_key = str(uuid.uuid4())
    #             cache.set(sociallogin_key, sociallogin.serialize(), timeout=600)  # Store for 10 minutes
    #             request.session['sociallogin_key'] = sociallogin_key
    #             print('select_user_type')
    #             return redirect('select_user_type')


    # def get_existing_user(self, user):
    #     # Check if a user with the given email already exists
    #     User = get_user_model()
    #     try:
    #         return User.objects.get(email=user.email)
    #     except User.DoesNotExist:
    #         return None

    # def save_user(self, request, sociallogin, form=None):
    #     user = sociallogin.user
    #     user_type = request.session.pop('user_type', None)
    #     if user_type:
    #         user.user_type = user_type
    #     return super(MySocialAccountAdapter, self).save_user(request, sociallogin, form)
