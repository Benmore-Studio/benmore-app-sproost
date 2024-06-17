# adapters.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from django.shortcuts import redirect
from django.contrib.auth import get_user_model


class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin: SocialLogin):
        user = sociallogin.user
        print(1)
        if not user.id:  # If user doesn't exist yet
            existing_user = self.get_existing_user(user)
            if existing_user:
                sociallogin.connect(request, existing_user)
                print(2)
            else:
                print(3)
                request.session['sociallogin'] = sociallogin.serialize()  # Save social login data in session

    def get_existing_user(self, user):
        print(4)
        User = get_user_model()
        print(5)
        try:
            return User.objects.get(email=user.email)
        except User.DoesNotExist:
            return None

    def save_user(self, request, sociallogin, form=None):
        print(6)
        user = sociallogin.user
        user_type = request.session.pop('user_type', None)
        if user_type:
            user.user_type = user_type
        print(8)
        return super(MySocialAccountAdapter, self).save_user(request, sociallogin,  form)