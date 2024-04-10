from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class MediaTypes(models.TextChoices):
    image = "Image"
    file = "File"


def file_upload_location(instance, filename):
    
    return f'files/{instance.object_id}/{filename}'


class Media(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="media")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    media_type = models.CharField(max_length=255, choices=MediaTypes.choices)
    file_path = models.FileField(upload_to=file_upload_location)
    upload_date = models.DateTimeField(auto_now_add=True, null=False)
