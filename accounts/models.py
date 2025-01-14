from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.text import slugify
from django.utils.crypto import get_random_string

from phonenumber_field.modelfields import PhoneNumberField
from quotes.models import Project

from django.utils.timezone import now
from datetime import timedelta




USER_TYPE_CHOICES_FOR_ACCOUNT_CREATION = (
        ('HO', 'Home Owner'),
        ('CO', 'Contractor'),
        ('AG', 'Agent'),
        ('IV', 'Investor')
    )
 

class User(AbstractUser):
    phone_number = PhoneNumberField(null=True, blank=True)
    user_type = models.CharField(max_length = 3, choices = USER_TYPE_CHOICES_FOR_ACCOUNT_CREATION)
    date_joined = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(
        blank=True,
        null=True,
        unique=True, 
        max_length=100, 
        allow_unicode=True) 
    email = models.EmailField(null=True, blank=True, db_index=True, unique=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            slug_base = f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
            base_slug = slugify(slug_base, allow_unicode=True)
            unique_slug = base_slug
            count = 1
            while User.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{get_random_string(4)}"
                count += 1
            self.slug = unique_slug
        
        super().save(*args, **kwargs)



class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def is_valid(self):
        """Check if OTP is still valid."""
        return now() <= self.expires_at
    
    def __str__(self):
        return f'{self.otp_code}'


