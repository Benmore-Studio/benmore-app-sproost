import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.fields import GenericRelation
# from profiles.models import AgentProfile, UserProfile

class QuoteRequestStatus(models.TextChoices):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"

class QuoteRequestManager(models.Manager):
    @property
    def latest_quote(self):
        return self.order_by('-id').first()

class QuoteRequest(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=False, related_name="quote_requests", help_text='created_by_home_owners')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=255, null=False)
    summary = models.TextField(null=False, max_length=257)
    status = models.CharField(max_length=255, choices=QuoteRequestStatus.choices, default=QuoteRequestStatus.pending, null=False)
    contact_phone = models.CharField(max_length=20, null=False)
    contact_email = models.EmailField(max_length=255, null=False)
    property_address = models.CharField(max_length=255, null=False)
    upload_date = models.DateTimeField(auto_now_add=True, null=False)
    media_paths = GenericRelation("main.Media")
    is_quote = models.BooleanField(default=True)
    
    created_by_agent = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, blank=True, null=True, related_name='agent_quote_requests')
    
    # created_by_homeowner = models.Forei/gnKey(UserProfile, on_delete=models.SET_NULL, blank=True, null=True, related_name='homeowner_quote_requests')
    
    
    objects = QuoteRequestManager()
    
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
    quote_request = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, null=False, related_name='quote_project')
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