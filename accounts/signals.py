from django.db.models.signals import post_save, post_delete, m2m_changed
from main.models import Media
from quotes.models import Property
from profiles.models import ContractorProfile
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
    Delete all media associated with the property when the property is deleted.
    """
    print("propertymedia deleted")
    related_media = Media.objects.filter(content_type__model='property', object_id=instance.id)
    related_media.delete()

@receiver(post_delete, sender=ContractorProfile)
def delete_media_on_contractorprofile_delete(sender, instance, **kwargs):
    """
    Delete all media associated with the contractor_profile when the contractor_profile is deleted.
    """
    related_media = Media.objects.filter(content_type__model='contractor_profile', object_id=instance.id)
    related_media.delete()