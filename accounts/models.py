from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

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