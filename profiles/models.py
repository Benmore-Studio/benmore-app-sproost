from django.db import models
from accounts.models import User
from address.models import AddressField
from django.contrib.contenttypes.fields import GenericRelation

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'user_profile')
    address = AddressField()
    city = models.CharField(max_length = 50, null = True, blank = True)
    state_province = models.CharField(max_length = 50, null = True, blank = True)    
    
    def __str__(self):
        return self.user.email


class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'contractor_profile')
    company_name = models.CharField(max_length = 255)
    registration_number = models.CharField(max_length = 225)
    specialization = models.CharField(max_length = 225, null = True, blank = True)
    company_address = AddressField()
    city = models.CharField(max_length = 50)
    media_paths = GenericRelation("main.Media")
    
    def __str__(self):
        return self.user.email
    
    
