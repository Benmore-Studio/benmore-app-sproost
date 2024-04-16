from django.db import models
from address.models import AddressField
from phonenumber_field.modelfields import PhoneNumberField

from quotes.models import Project


class Property(models.Model):
    assigned_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True,  related_name='assigned_properties_by')
    assigned_to = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True,  related_name='assigned_properties_to')
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='properties_project')
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = 'Properties'
    
    def __str__(self) -> str:
        return str(self.project.quote_request.title)
        
    def save(self, *args, **kwargs):
        if self.assigned_to and not self.assigned_to.user_type in ['HO', 'AG']:
            raise ValueError('Only Home Owners can be assigned properties')
        super().save(*args, **kwargs)