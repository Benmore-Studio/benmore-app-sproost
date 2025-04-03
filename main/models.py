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


class MessageMediaTypes(models.TextChoices):
    IMAGE = "image", _("Image")
    FILE = "file", _("File")
    VIDEO = "video", _("Video")

    
class ImageCategories(models.TextChoices):
    BEFORE = "before", _("Before")
    AFTER = "after", _("After")


    
class ImageCategories(models.TextChoices):
    BEFORE = "before", _("Before")
    AFTER = "after", _("After")


   
    
class Media(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name="media")
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    file_url = models.URLField(max_length=1024, blank=True, null=True)
    public_id = models.CharField(max_length=255, blank=True, null=True)
    media_type = models.CharField(max_length=10, choices=MediaTypes.choices, default=MediaTypes.IMAGE)
    image = models.ImageField(upload_to=image_upload_location, null=True, blank=True)
    image_category = models.CharField(max_length=10, choices=ImageCategories.choices, null=True, blank=True, default=ImageCategories.BEFORE)
    file = models.FileField(upload_to=file_upload_location, null=True, blank=True, storage=RawMediaCloudinaryStorage())
    video = models.FileField(upload_to=video_upload_location, null=True, blank=True, storage=RawMediaCloudinaryStorage())  # Add this field
    upload_date = models.DateTimeField(auto_now_add=True, null=False)

    def __str__(self):
        return f"{self.content_object} - Media"


class MessageMedia(models.Model):
    message = models.ForeignKey("chat.Message", on_delete=models.CASCADE, related_name="messagemedia", db_index=True)
    file_url = models.URLField(max_length=1024)
    public_id = models.CharField(max_length=255)
    media_type = models.CharField(max_length=20, choices=MessageMediaTypes.choices, default=MessageMediaTypes.IMAGE)
    file_name = models.CharField(max_length=255, blank=True, null=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    thumbnail_url = models.URLField(max_length=1024, blank=True, null=True)
    upload_date = models.DateTimeField(auto_now_add=True, null=False)

