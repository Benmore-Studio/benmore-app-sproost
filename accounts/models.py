from django.contrib.auth.models import AbstractUser
from django.db import models

from phonenumber_field.modelfields import PhoneNumberField
from quotes.models import Project

class UserTypes(models.TextChoices):
    home_owner = "home-owner"
    contractor = "contractor"
    agent = "agent"
    investor = "investor"

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
    slug = models.SlugField(
        blank=True,
        null=True,
        unique=True, 
        max_length=100, 
        allow_unicode=True) 
    
