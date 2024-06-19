from allauth.socialaccount.models import SocialLogin
from django.core.cache import cache


def stash_sociallogin(request, sociallogin):
    data = sociallogin.serialize()
    request.session['sociallogin'] = data

def retrieve_sociallogin(request):
    sociallogin_key = request.session.get('sociallogin_key')
    if sociallogin_key:
        data = cache.get(sociallogin_key)
        if data:
            return SocialLogin.deserialize(data)
    return None
