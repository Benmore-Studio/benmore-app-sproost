from django.db import models
from address.models import AddressField
from phonenumber_field.modelfields import PhoneNumberField


class Property(models.Model):
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True,  related_name='assigned_properties')
    name = models.CharField(max_length=100)
    address = AddressField()
    phone_number = PhoneNumberField()
    email = models.EmailField()
    is_assigned = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Properties'
    
    def __str__(self) -> str:
        if self.assigned_by:
            return self.assigned_by.email + " " + self.name
        return self.name
        
    def save(self, *args, **kwargs):
        if self.assigned_by and not self.assigned_by.user_type in ['HO', 'AG']:
            raise ValueError('Only Home Owners can be assigned properties')
        super().save(*args, **kwargs)