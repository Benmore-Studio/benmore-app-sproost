from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
# from versatileimagefield.fields import VersatileImageField

def file_upload_location(instance, filename):
    
    return f'file/{instance.object_id}/{filename}'

def image_upload_location(instance, filename):
    
    return f'images/{instance.object_id}/{filename}'


class MediaTypes(models.TextChoices):
    image = "Image"
    file = "File"



class Media(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="media")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    image = models.ImageField(upload_to=image_upload_location, null=True)
    file = models.FileField(upload_to=file_upload_location, null=True)
    upload_date = models.DateTimeField(auto_now_add=True, null=False)
