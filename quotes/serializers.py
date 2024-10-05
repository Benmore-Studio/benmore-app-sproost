from rest_framework import serializers
from .models import Project
from quotes.models import QuoteRequest
from main.models import Media
from django.contrib.contenttypes.models import ContentType


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  

class QuoteRequestAllSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuoteRequest
        fields = '__all__'  


class QuoteRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Quote Requests, handling media file uploads as well.
    
    ----------------------------
    INPUT PARAMETERS:
    - title: Title of the quote request.
    - summary: A summary of the quote request.
    - contact_phone: Contact phone of the user.
    - contact_username: Username of the user.
    - property_address: Address of the property.
    - created_by_agent: The agent creating the quote request (optional).
    - media: List of media files (image, file, etc.).
    
    -----------------------------
    OUTPUT PARAMETERS:
    - Serialized data for quote request including file uploads.
    """
    
    media = serializers.ListField(
        child=serializers.FileField(), required=False, allow_empty=True
    )

    class Meta:
        model = QuoteRequest
        fields = [
            'title', 'summary', 'contact_phone', 
            'contact_username', 'property_address', 
            'quote_for', 'media'
        ]
    def create(self, validated_data):
            """
            Handles the creation of a new quote request, including file uploads.

            If there are media files, they will be attached to the quote request.
            """
            media_files = validated_data.pop('media', None)
            quote_request = QuoteRequest.objects.create(**validated_data)

            # If media files are present, save each media file and associate it with the QuoteRequest
            if media_files:
                content_type = ContentType.objects.get_for_model(quote_request)
                for media_file in media_files:
                    # Determine the media type based on file type (image, video, etc.)
                    if media_file.content_type.startswith('image'):
                        media_type = 'Image'
                    elif media_file.content_type.startswith('video'):
                        media_type = 'Video'
                    else:
                        media_type = 'File'

                    # Create a Media object and associate it with the QuoteRequest via GenericForeignKey
                    Media.objects.create(
                        content_type=content_type,
                        object_id=quote_request.id,
                        media_type=media_type,
                        image=media_file if media_type == 'Image' else None,
                        file=media_file if media_type == 'File' else None,
                        video=media_file if media_type == 'Video' else None
                    )

            return quote_request

