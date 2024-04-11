import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.contenttypes.fields import GenericRelation

class QuoteRequestStatus(models.TextChoices):
    pending = "Pending"
    approved = "Approved"


class QuoteRequest(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=False)
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
    
    def __str__(self) -> str:
        return self.title

def upload_location(instance, filename):
    # file will be uploaded to MEDIA_ROOT/projects/<project_id>/<filename>
    return 'projects/{0}/{1}'.format(instance.project_id, filename)


class Project(models.Model):
    admin = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    quote_request = models.ForeignKey(QuoteRequest, on_delete=models.CASCADE, null=False, related_name='quote_project')
    file = models.FileField(upload_to=upload_location, null=True, blank=True)
    is_approved = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if self.is_approved: 
            self.is_approved = True 
            self.quote_request.is_quote = False
            self.quote_request.save()  

        super(Project, self).save(*args, **kwargs)

    
    def __str__(self) -> str:
        return str(self.quote_request.title)