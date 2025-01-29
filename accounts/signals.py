from django.db.models.signals import post_save, post_delete, m2m_changed
from main.models import Media
from quotes.models import Property
from django.dispatch import receiver
from allauth.socialaccount.signals import social_account_added

import logging

logger = logging.getLogger(__name__)

@receiver(social_account_added)
def handle_social_account_added(request, sociallogin, **kwargs):
    # Perform actions when a social account is connected
    if sociallogin.account.provider == 'google':
        user = sociallogin.user
        # Here you can perform actions like setting user type or any other logic
        # print(f"User {user} signed up with Google!")
        logger.info(f"User {user} signed up with Google!")


@receiver(post_delete, sender=Property)
def delete_media_on_event_delete(sender, instance, **kwargs):
    """
    Delete all media associated with the event when the event is deleted.
    """
    related_media = Media.objects.filter(content_type__model='event', object_id=instance.id)
    related_media.delete()