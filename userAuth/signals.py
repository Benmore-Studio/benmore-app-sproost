from allauth.account.signals import user_signed_up
from django.dispatch import receiver
from .models import UserProfile

@receiver(user_signed_up)
def create_profile(request, user, **kwargs):
    UserProfile.objects.get_or_create(user=user)