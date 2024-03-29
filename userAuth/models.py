from django.contrib.auth.models import User
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('HO', 'Home Owner'),
        ('CO', 'Contractor'),
        ('AG', 'Agent'),
        ('IV', 'Investor')
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name = 'profile')
    phone_number = PhoneNumberField(null = True, blank = True)
    user_type = models.CharField(max_length = 3, choices = USER_TYPE_CHOICES,  null = True, blank = True)
    home_address = models.CharField(max_length = 255, null = True, blank = True)
    city = models.CharField(max_length = 255, null = True, blank = True)
    state = models.CharField(max_length = 255, null = True, blank = True)
    
    
    def __str__(self):
        return self.user.username