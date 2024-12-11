from django.db import models
from accounts.models import User
from address.models import AddressField
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _


def image_upload_location_home_owner(instance, filename):
    return f'home_ownerprofile/{instance.id}/{filename}'
    
def image_upload_location_agent(instance, filename):
    return f'agentprofile/{instance.id}/{filename}'
    
def image_upload_location_contractor(instance, filename):
    return f'contractorprofile/{instance.id}/{filename}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'user_profile')
    address = models.CharField(max_length = 50,null = True)
    city = models.CharField(max_length = 50, null = True, blank = True)
    state_province = models.CharField(max_length = 50, null = True, blank = True)
    image = models.ImageField(upload_to=image_upload_location_home_owner, null=True) 
   
    
    def __str__(self):
        return self.user.email


class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'agent_profile')
    address = models.CharField(max_length = 50, default='Nigeria')
    registration_ID = models.CharField(max_length = 225, default='12345678', unique=True, verbose_name="license number", help_text='Also known as licences_ID')
    image = models.ImageField(upload_to=image_upload_location_agent, null=True)
    country= models.CharField(max_length=500, default='Nigeria')
    
    def __str__(self):
        return self.user.email


class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'contractor_profile')
    company_name = models.CharField(max_length = 255, default='belize')
    specialization = models.CharField(max_length = 225, default='coding')
    company_address = models.CharField(max_length = 50, default='Nigeria')
    insurance_number = models.CharField(max_length=255, default='12345678')
    license_number= models.CharField(max_length=225, default='12345678')
    country= models.CharField(max_length=225, default='Nigeria')
    website = models.URLField(max_length=255, null=True)
    city = models.CharField(max_length = 50, null = True, blank = True)
    media_paths = GenericRelation("main.Media")
    image = models.ImageField(upload_to=image_upload_location_contractor, null=True)

    def __str__(self):
        return self.user.email
    
class InvestorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'investor_profile')
    company_name = models.CharField(max_length = 255)
    specialization = models.CharField(max_length = 225)
    company_address = models.CharField(max_length = 50)
    country= models.CharField(max_length=225)
    media_paths = GenericRelation("main.Media")
    image = models.ImageField(upload_to=image_upload_location_contractor, null=True)

    def __str__(self):
        return self.user.email
    
    

class Referral(models.Model):
    """Represents a referral made by a user.

    Attributes:
        referrer (User): The user who made the referral.
        referred (User): The users who have been referred.
        code (str): The referral code.
    """
    referrer = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='referrer',
        help_text=_('The user who made the referral.')
    )
    referred = models.ManyToManyField(
        User,
        related_name='referred',
        help_text=_('The users who have been referred.')
    )
    code = models.CharField(
        max_length=100,
        help_text=_('The referral code.')
    )

    class Meta:
        verbose_name = _('Referral')
        verbose_name_plural = _('Referrals')

    def __str__(self):
        return self.referrer.email



