from django.db import models
from address.models import AddressField
from phonenumber_field.modelfields import PhoneNumberField


class Property(models.Model):
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    address = AddressField()
    phone_number = PhoneNumberField()
    email = models.EmailField()
    is_assigned = models.BooleanField(default=False)
    
    
    def __str__(self) -> str:
        self.assigned_by.email
        
    def save(self, *args, **kwargs):
        if self.assigned_by.user_type != 'HO':
            raise ValueError('Only Home Owners can be assigned properties')
        super().save(*args, **kwargs)