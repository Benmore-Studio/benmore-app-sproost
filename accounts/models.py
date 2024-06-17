from django.contrib.auth.models import AbstractUser
from django.db import models

from django.utils.text import slugify
from django.utils.crypto import get_random_string

from phonenumber_field.modelfields import PhoneNumberField
from quotes.models import Project

from django.utils.text import slugify
from django.utils.crypto import get_random_string

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
    
    # def save(self, *args, **kwargs):
    #     if not self.slug:
    #         slug_base = f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username
    #         self.slug = slugify(slug_base, allow_unicode=True)
    #         while User.objects.filter(slug=self.slug).exists():
    #             self.slug = f"{slugify(slug_base, allow_unicode=True)}-{get_random_string(4)}"
    #     super().save(*args, **kwargs)



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
