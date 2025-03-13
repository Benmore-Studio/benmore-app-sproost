from rest_framework import serializers
from .models import Project
from quotes.models import QuoteRequest, QuoteRequestStatus, UserPoints
from main.models import Media
from django.contrib.contenttypes.models import ContentType
from accounts.models import User
from property.serializers import PropertyRetrieveSerializer


 


def handle_media_files(instance, media_files):
    """
    Handles the saving of media files and associates them with the provided instance.
    """
    if media_files:
        content_type = ContentType.objects.get_for_model(instance)
        for media_file in media_files:
            # Determine the media type based on file type (image, video, etc.)
            if media_file.content_type.startswith('image'):
                media_type = 'Image'
            elif media_file.content_type.startswith('video'):
                media_type = 'Video'
            else:
                media_type = 'File'

            # Create a Media object and associate it with the instance via GenericForeignKey
            Media.objects.create(
                content_type=content_type,
                object_id=instance.id,
                media_type=media_type,
                image=media_file if media_type == 'Image' else None,
                file=media_file if media_type == 'File' else None,
                video=media_file if media_type == 'Video' else None
            )



class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  

class QuoteRequestAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = '__all__'  



class QuoteRequestSerializer(serializers.ModelSerializer):
    media = serializers.ListField(
        child=serializers.FileField(), required=False, allow_empty=True
    )
    property = PropertyRetrieveSerializer(read_only=True)  

    class Meta:
        model = QuoteRequest
        fields = "__all__"
    
    def create(self, validated_data):
        media_files = validated_data.pop('media', None)
        quote_request = QuoteRequest.objects.create(**validated_data)
        handle_media_files(quote_request, media_files)

       
        return quote_request



    



 
    