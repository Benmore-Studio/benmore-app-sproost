from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

class QuoteRequestsStatus(models.TextChoices):
    pending = "Pending"
    approved = "Approved"


class QuoteRequests(models.Model):
    user = models.ForeignKey("accounts.User", on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=255, null=False)
    summary = models.TextField(null=False, max_length=257)
    status = models.CharField(max_length=255, choices=QuoteRequestsStatus.choices, default=QuoteRequestsStatus.pending, null=False)
    contact_phone = models.CharField(max_length=20, null=False)
    contact_email = models.EmailField(max_length=255, null=False)
    property_address = models.CharField(max_length=255, null=False)
    upload_date = models.DateTimeField(auto_now_add=True, null=False)
    media_paths = models.ForeignKey("main.Media", on_delete=models.SET_NULL, null=True)


class Projects(models.Model):
    admin = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    quote_request = models.ForeignKey(QuoteRequests, on_delete=models.CASCADE, null=False)
