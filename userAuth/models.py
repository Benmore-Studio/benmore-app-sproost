from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from address.models import AddressField

USER_TYPE_CHOICES = (
        ('HO', 'Home Owner'),
        ('CO', 'Contractor'),
        ('AG', 'Agent'),
        ('IV', 'Investor')
    )
 
class User(AbstractUser):
    phone_number = PhoneNumberField(null=False, blank=False)
    user_type = models.CharField(max_length = 3, choices = USER_TYPE_CHOICES)
    date_joined = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'user_profile')
    address = AddressField()
    city = models.CharField(max_length = 50, null = True, blank = True)
    state_province = models.CharField(max_length = 50, null = True, blank = True)
    
    
    def __str__(self):
        return self.user.username

class ContractorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'contractor_profile')
    company_name = models.CharField(max_length = 255)
    registration_number = models.CharField(max_length = 225)
    specialization = models.CharField(max_length = 225, null = True, blank = True)
    company_address = AddressField()
    city = models.CharField(max_length = 50)
    
    