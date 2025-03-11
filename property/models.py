from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

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
        
        
class PropertyTypeChoices(models.TextChoices):
    HOUSE = 'house', _('House')
    APARTMENT = 'apartment', _('Apartment')
    CONDOMINIUM = "condominium", _("Condominium")
    TOWNHOUSE = "townhouse", _("Townhouse")
    COMMERCIAL = "commercial", _("Commercial")


GARAGE_CHOICES = (
    ('attached', 'Attached'),
    ('detached', 'Detached'),
    ('none', 'None'),
)

class PropertyStatusChoices(models.TextChoices):
    PENDING = 'pending', _('Pending')
    IN_PROGRESS = 'in-progress', _('In Progress')
    COMPLETED = 'completed', _('Completed')


class Property(models.Model):
    title = models.CharField(max_length=255, blank=True)
    property_type = models.CharField(
        max_length=20,
        choices=PropertyTypeChoices.choices,
        default=PropertyTypeChoices.HOUSE
    )
    property_owner = models.ForeignKey(
        "accounts.User",
        blank=True,
        on_delete=models.CASCADE,
        related_name='owned_properties'
    )
    home_owner_agents = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name='home_owner_agents'
    )
    contractors = models.ManyToManyField(
        "profiles.ContractorProfile",
        blank=True,
        related_name="assigned_contractors",
        help_text=_("Contractors assigned to this property.")
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)
    address = models.CharField(max_length=255, blank=True)
    half_bath = models.PositiveIntegerField(null=True, blank=True)
    full_bath = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    square_footage = models.PositiveIntegerField(null=True, blank=True)
    total_square_foot = models.PositiveIntegerField(null=True, blank=True)
    lot_size = models.PositiveIntegerField(null=True, blank=True)
    scope_of_work = models.TextField(default='explain your scope of work')
    taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    basement_details = models.TextField(null=True, blank=True)
    garage = models.CharField(max_length=50, choices=GARAGE_CHOICES, null=True, blank=True)
    media_paths = GenericRelation("main.Media")  # Assumes Media is in main.models
    repair_recommendations = models.TextField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)
    likes = models.ManyToManyField(
        "accounts.User",
        related_name="liked_properties",
        blank=True,
        help_text=_("Investors who have liked this property.")
    )
    status = models.CharField(
        max_length=20,
        choices=PropertyStatusChoices.choices,
        default=PropertyStatusChoices.PENDING,
        help_text=_("Status: Pending (new listing), In Progress (contractor assigned), Completed (work finished).")
    )
    
    is_first_property = models.BooleanField(
        default=True,
        help_text=_("Indicates if this is the property owner's first property.")
    )
    
    has_quotes = models.BooleanField(
        default=False,
        help_text=_("Indicates if the property has a quotes on it.")
    )
    

    def __str__(self):
        return f"{self.property_owner} - {self.address}"