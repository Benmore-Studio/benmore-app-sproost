import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import gettext_lazy as _

# from profiles.models import AgentProfile, UserProfile


def upload_location_quote(instance, filename):
    # file will be uploaded to MEDIA_ROOT/projects/<project_id>/<filename>
    return 'quotes/{0}/{1}'.format(instance.id, filename)



RENOVATION_CHOICES=(
    ('interior','Interior'),
    ('exterior', 'Exterior'),
    )

QUOTE_REQUEST_TYPE=(
    ('RTS','Renovate To Sell'),
    ('RTR', 'ExterioRenovate To Rent'),
    ('RTO', 'ExterioRenovate To Own'),
    )



GARAGE_CHOICES=(
    ('pending','Pending'),
    )


class QuoteRequestStatus(models.TextChoices):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"


    
class Renovation(models.Model):
    type = models.CharField(max_length=50, choices=RENOVATION_CHOICES)
    status = models.CharField(max_length=50, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed')])
    budget = models.IntegerField()
    timeline = models.CharField(max_length=500, null=True, blank=True)


class Property(models.Model):
    tittle = models.CharField(max_length=255)
    property_owner = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='property_owner')
    home_owner_agents = models.ManyToManyField("accounts.User", blank=True, related_name='home_owner_agents')
    contractors = models.ManyToManyField(
        "accounts.User",
        blank=True,
        related_name="assigned_contractors",
        help_text=_("Contractors assigned to this property.")
    )
    renovation = models.OneToOneField(Renovation, on_delete=models.CASCADE, related_name='renovations', null=True, blank=True)
    address = models.CharField(max_length=255)
    half_bath = models.PositiveIntegerField(null=True, blank=True)
    full_bath = models.PositiveIntegerField(null=True, blank=True)
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    square_footage = models.PositiveIntegerField(null=True, blank=True)
    total_square_footage = models.PositiveIntegerField(null=True, blank=True)
    lot_size = models.PositiveIntegerField(null=True, blank=True)
    taxes = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    basement_details = models.TextField(null=True, blank=True)
    garage = models.CharField(max_length=50, choices=GARAGE_CHOICES, null=True, blank=True)
    media_paths = GenericRelation("main.Media")
    date_created = models.DateField(auto_now_add=True)
    likes = models.ManyToManyField(
        "accounts.User",
        related_name="liked_properties",
        blank=True,
        help_text=_("investors who have liked this properties.")
    )

    def __str__(self):
        return f"{self.property_owner} - {self.address}"


class QuoteRequest(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name="quote_requests", help_text='the user who created the quote')
    contractors = models.ForeignKey("profiles.ContractorProfile", null=True, blank=True, on_delete=models.PROTECT, related_name="quote_contractors")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="quote_properties")
    property_type = models.CharField(max_length=50, choices=RENOVATION_CHOICES)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, )
    summary = models.TextField(null=False, max_length=257)
    status = models.CharField(max_length=255, choices=QuoteRequestStatus.choices, default=QuoteRequestStatus.pending)
    quote_type = models.CharField(max_length=355, choices=QUOTE_REQUEST_TYPE)
    contact_phone = models.CharField(max_length=20, null=False)
    upload_date = models.DateTimeField(auto_now_add=True, null=False)
    is_quote = models.BooleanField(default=True)
    media_paths = GenericRelation("main.Media")
    file = models.FileField(upload_to=upload_location_quote, null=True, blank=True)  

    def assign_contractor(self, contractor):
        """Assign a contractor and update the property status to 'in_progress'."""
        self.contractors = contractor
        self.save()
        self.property.contractors.add(contractor)
        self.property.status = "in_progress"
        self.property.save()

    def complete_project(self):
        """Mark the property as completed."""
        self.property.status = "completed"
        self.property.save()  
    
    # objects = QuoteRequestManager()
    
    def __str__(self) -> str:
        return self.title
    
    # def save(self, *args, **kwargs): 
    #     if not self.slug:
    #         slug_name= slugify(self.title) + result + local_time.strftime("%Y-%m-%d-%H-%M-%S")
    #         self.slug =  slug_name  

    # a method that retuns the last in the querset of QuoteRequest
    

def upload_location(instance, filename):
    # file will be uploaded to MEDIA_ROOT/projects/<project_id>/<filename>
    return 'projects/{0}/{1}'.format(instance.id, filename)




class Project(models.Model):  
    admin = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    file = models.FileField(upload_to=upload_location, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    @property
    def admin_pdf(self):
        if self.file:
            return self.file.url
        return ""
    
    def save(self, *args, **kwargs):
        if self.is_approved: 
            self.is_approved = True 
            self.quote_request.is_quote = False
            self.quote_request.status = QuoteRequestStatus.approved
            self.quote_request.save()  

        super(Project, self).save(*args, **kwargs)
    
    def __str__(self) -> str:
        return str(self.quote_request.title)


class Referral(models.Model):
    referrer = models.ForeignKey("accounts.User", related_name='referrals', on_delete=models.CASCADE)
    referred_user = models.OneToOneField("accounts.User", related_name='referred_by', on_delete=models.CASCADE, null=True, blank=True)
    referral_code = models.CharField(max_length=12, unique=True)
    date_created = models.DateTimeField(auto_now_add=True)

class UserPoints(models.Model):
    user = models.OneToOneField("accounts.User", on_delete=models.CASCADE, related_name='points')
    total_points = models.PositiveIntegerField(default=0)

    def add_points(self, points):
        self.total_points += points
        self.save()


class Bid(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='bids')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='bids')
    bid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_winner = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bid by {self.user.username} for {self.project.name} - {'Winner' if self.is_winner else 'Pending'}"


class ProjectPictures(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, related_name='pictures')
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='pictures')
    image = models.ImageField(upload_to='project_pictures/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Picture by {self.user.username} for project {self.project.name}"


class Review(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    contractor = models.ForeignKey(
        'profiles.ContractorProfile',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.PositiveSmallIntegerField()  
    comments = models.TextField(blank=True)  # Comments are optional
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.contractor.user.username}"


class QuoteRequestManager(models.Manager):
    @property
    def latest_quote(self):
        return self.order_by('-id').first()

#region property comment
# class Property(models.Model):
#     renovation = models.OneToOneField(Renovation, on_delete=models.CASCADE, related_name='renovations')
#     property_type = models.CharField(max_length=50)
#     address = models.CharField(max_length=50, choices=RENOVATION_CHOICES)
#     half_bath = models.IntegerField(null=True, blank=True)
#     full_bath = models.IntegerField(null=True, blank=True)
#     beds = models.IntegerField(null=True, blank=True)
#     bedroom = models.IntegerField(null=True, blank=True)
#     sqr_fit = models.IntegerField(null=True, blank=True)
#     total_sqr = models.IntegerField(null=True, blank=True)
#     above_sqr = models.IntegerField(null=True, blank=True)
#     below_sqr = models.IntegerField(null=True, blank=True)
#     lot = models.IntegerField(null=True, blank=True)
#     lot_size = models.IntegerField(null=True, blank=True)
#     taxes = models.IntegerField(null=True, blank=True)
#     status = models.CharField(max_length=50, choices=PROJECT_STATUS, default='pending' )
#     basement = models.CharField(max_length=500, null=True, blank=True)
#     basement = models.CharField(max_length=500, null=True, blank=True)
#     basement = models.CharField(max_length=500, null=True, blank=True)
#     date_created = models.DateField()
#     garage = models.CharField(max_length=50, choices=GARAGE_CHOICES)

#endregion






   

