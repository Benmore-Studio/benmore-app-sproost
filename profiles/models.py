import uuid
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
    home_owner_invited_agents = models.ManyToManyField(User, related_name = 'invited_agents', blank=True)
    home_owner_associated_contarctors = models.ManyToManyField(User, related_name = 'associated_contarctors', blank=True)
    home_owner_address = models.CharField(max_length = 50,null = True)
    city = models.CharField(max_length = 50, null = True, blank = True)
    state_province = models.CharField(max_length = 50, null = True, blank = True)
    image = models.ImageField(upload_to=image_upload_location_home_owner, null=True) 
   
    
    def __str__(self):
        return self.user.email


class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'agent_profile')
    agent_invited_home_owners = models.ForeignKey(User, on_delete=models.SET_NULL, related_name = 'invited_home_owners', null=True, blank=True)
    agent_associated_contarctors = models.ForeignKey(User, on_delete=models.SET_NULL, related_name = 'agent_associated_contarctors', null=True, blank=True)
    agent_address = models.CharField(max_length = 50)
    registration_ID = models.CharField(max_length = 225, unique=True, verbose_name="license number", help_text='Also known as licences_ID')
    image = models.ImageField(upload_to=image_upload_location_agent, null=True)
    country= models.CharField(max_length=500)
    
    def __str__(self):
        return self.user.email


class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'contractor_profile')
    company_name = models.CharField(max_length = 255)
    specialization = models.CharField(max_length = 225)
    company_address = models.CharField(max_length = 50)
    insurance_number = models.CharField(max_length=25)
    license_number= models.CharField(max_length=225 )
    country= models.CharField(max_length=225)
    bio= models.CharField(max_length=500, null = True, blank = True)
    tags= models.CharField(max_length=500, null = True, blank = True)
    website = models.URLField(max_length=255, null=True)
    address = models.CharField(max_length = 50, null = True, blank = True)
    hired = models.IntegerField(default=0)
    employees = models.IntegerField(default=0)
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
    
    
    
class Invitation(models.Model):
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitations') # for agents to agents
    email = models.EmailField()
    referral_code = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Generate a referral code if not provided
        if not self.referral_code:
            self.referral_code = str(uuid.uuid4()).replace('-', '')[:10]
        super().save(*args, **kwargs)


class Message(models.Model):
    content = models.TextField(max_length=512)
    sender= models.ForeignKey(User, on_delete=models.CASCADE, related_name="messagesender")
    receiver= models.ForeignKey(User, on_delete=models.CASCADE, related_name="messagereceiver")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['sender', 'receiver'])
        ]

    def __str__(self):
        return f'{self.content}'

