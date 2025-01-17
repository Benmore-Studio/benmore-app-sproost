from django.db import models
from address.models import AddressField
from phonenumber_field.modelfields import PhoneNumberField

from quotes.models import Project

class AssignedAccount(models.Model):
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True,  related_name='assigned_properties_by')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.CASCADE, null=True, blank=True,  related_name='assigned_properties_to')
    is_approved = models.BooleanField(default=False)

    
    
    def __str__(self) -> str:
        return f'{self.assigned_to} assigned by {self.assigned_by}'
        
    def save(self, *args, **kwargs):
        if self.assigned_to and not self.assigned_to.user_type == 'AG':
            raise ValueError('Only Home Agent can be assigned properties')
        if self.assigned_by and not self.assigned_by.user_type in ['HO', 'AG']:
            raise ValueError('Only Home Owners and Agents can be assigned properties')
        super().save(*args, **kwargs)