from rest_framework import serializers
from .models import Project
from quotes.models import QuoteRequest, QuoteRequestStatus, Property
from main.models import Media
from django.contrib.contenttypes.models import ContentType
 


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


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = '__all__' 

    def create(self, validated_data):
        """
        Handles the creation of a new quote request, including file uploads.
        """
        media_files = validated_data.pop('media', None)
        quote_request = Property.objects.create(**validated_data)
        
        # Call the utility function to handle media files
        handle_media_files(quote_request, media_files)

        return quote_request

class QuoteRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for Quote Requests, handling media file uploads as well.
    
    ----------------------------
    INPUT PARAMETERS:
    - title: Title of the quote request.
    - summary: A summary of the quote request.
    - contact_phone: Contact phone of the user.
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
            'contractors','property', 'media'
        ]
    def create(self, validated_data):
        """
        Handles the creation of a new quote request, including file uploads.
        """
        media_files = validated_data.pop('media', None)
        quote_request = QuoteRequest.objects.create(**validated_data)
        
        # Call the utility function to handle media files
        handle_media_files(quote_request, media_files)

        return quote_request


class QuoteStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=QuoteRequestStatus.choices, required=True)


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'content_type', 'object_id', 'media_type', 'image', 'file', 'video', 'upload_date']

    def validate(self, data):
        """
        Validate uploaded media types (files, images, videos).
        """
        supported_file_types = ['pdf', 'doc', 'docx', 'txt']
        supported_image_types = ['jpg', 'jpeg', 'png', 'gif']
        supported_video_types = ['mp4', 'avi', 'mov', 'mkv']

        file = data.get('file')
        image = data.get('image')
        video = data.get('video')

        if file:
            extension = file.name.split('.')[-1].lower()
            if extension not in supported_file_types:
                raise serializers.ValidationError({"file": f"Unsupported file type: {extension}"})

        if image:
            extension = image.name.split('.')[-1].lower()
            if extension not in supported_image_types:
                raise serializers.ValidationError({"image": f"Unsupported image type: {extension}"})

        if video:
            extension = video.name.split('.')[-1].lower()
            if extension not in supported_video_types:
                raise serializers.ValidationError({"video": f"Unsupported video type: {extension}"})

        return data

    def create(self, validated_data):
        """
        Create a single Media instance.
        """
        return Media.objects.create(**validated_data)

    def create_many(self, content_type, object_id, files, images, videos):
        """
        Handle multiple media uploads.
        """
        created_media = []
        errors = []

        # Process files
        for file in files:
            media_data = {
                'content_type': content_type.id,
                'object_id': object_id,
                'media_type': 'File',
                'file': file
            }
            serializer = MediaSerializer(data=media_data)
            if serializer.is_valid():
                created_media.append(serializer.save())
            else:
                errors.append(serializer.errors)

        # Process images
        for image in images:
            media_data = {
                'content_type': content_type.id,
                'object_id': object_id,
                'media_type': 'Image',
                'image': image
            }
            serializer = MediaSerializer(data=media_data)
            if serializer.is_valid():
                created_media.append(serializer.save())
            else:
                errors.append(serializer.errors)

        # Process videos
        for video in videos:
            media_data = {
                'content_type': content_type.id,
                'object_id': object_id,
                'media_type': 'Video',
                'video': video
            }
            serializer = MediaSerializer(data=media_data)
            if serializer.is_valid():
                created_media.append(serializer.save())
            else:
                errors.append(serializer.errors)

        return created_media, errors



