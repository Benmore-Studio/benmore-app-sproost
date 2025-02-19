from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from cloudinary_storage.storage import RawMediaCloudinaryStorage
from django.utils.translation import gettext_lazy as _

def file_upload_location(instance, filename):
    return f'files/{instance.object_id}/{filename}'

def image_upload_location(instance, filename):
    return f'images/{instance.object_id}/{filename}'

def video_upload_location(instance, filename):
    return f'videos/{instance.object_id}/{filename}'

class MediaTypes(models.TextChoices):
    IMAGE = "Image", _("Image")
    FILE = "File", _("File")
    VIDEO = "Video", _("Video")

   
    
class Media(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="media")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    file_url = models.URLField(max_length=1024, blank=True, null=True)
    public_id = models.CharField(max_length=255, blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MediaTypes.choices, default=MediaTypes.IMAGE)
    image = models.ImageField(upload_to=image_upload_location, null=True, blank=True)
    file = models.FileField(upload_to=file_upload_location, null=True, blank=True, storage=RawMediaCloudinaryStorage())
    video = models.FileField(upload_to=video_upload_location, null=True, blank=True, storage=RawMediaCloudinaryStorage())  # Add this field
    upload_date = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return f"{self.content_object} - Media"


