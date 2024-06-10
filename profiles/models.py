from django.db import models
from accounts.models import User
from address.models import AddressField
from django.contrib.contenttypes.fields import GenericRelation

def image_upload_location(instance, filename):
    return f'contractorprofile/{instance.id}/{filename}'


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'user_profile')
    address = AddressField(null = True)
    city = models.CharField(max_length = 50, null = True, blank = True)
    state_province = models.CharField(max_length = 50, null = True, blank = True) 
    # slug = models.SlugField(
    #     blank=True,
    #     null=True,
    #     unique=True, 
    #     max_length=100, 
    #     allow_unicode=True)   
    
    def __str__(self):
        return self.user.email

class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'agent_profile')
    address = AddressField(null = True)
    registration_ID = models.CharField(max_length = 225, null = True, blank = True, unique=True, verbose_name="license number", help_text='Also known as licences_ID')
    has_seen_onboarding_message = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.email


class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'contractor_profile')
    company_name = models.CharField(max_length = 255)
    registration_number = models.CharField(max_length = 225)
    specialization = models.CharField(max_length = 225, null = True, blank = True)
    company_address = AddressField(null =True)
    website = models.URLField(max_length=255, null=True)
    city = models.CharField(max_length = 50)
    media_paths = GenericRelation("main.Media")
    image = models.ImageField(upload_to=image_upload_location, null=True)

    def __str__(self):
        return self.user.email
    
    

class Referral(models.Model):
    referrer = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'referrer')
    referred = models.ManyToManyField(User, related_name = 'referred')
    code = models.CharField(max_length=100)
  
    
    def __str__(self):
        return self.referrer.email


