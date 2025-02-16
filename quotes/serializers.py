from rest_framework import serializers
from .models import Project
from quotes.models import QuoteRequest, QuoteRequestStatus, Property
from main.models import Media
from django.contrib.contenttypes.models import ContentType
from accounts.models import User

 


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
        fields = "__all__"
    
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


class BulkMediaSerializer(serializers.Serializer):
    """
    A custom serializer for handling multiple media uploads in one pass.
    """
    content_type_id = serializers.IntegerField()
    object_id = serializers.IntegerField()

    # We expect lists of uploaded files for each category
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        required=False
    )
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        required=False
    )

    def validate(self, attrs):
        """
        Perform extension and size checks for all media in a single pass.
        """
        max_file_size = 10 * 1024 * 1024
        supported_file_types = ['pdf', 'doc', 'docx', 'txt']
        supported_image_types = ['jpg', 'jpeg', 'png', 'gif']
        supported_video_types = ['mp4', 'avi', 'mov', 'mkv', 'ts']

        # We'll accumulate errors in a dict {field: [list of errors]}
        # but you could raise ValidationError immediately if you prefer.
        errors = {}

        def validate_file(f, kind):
            ext = f.name.split('.')[-1].lower()
            if kind == 'file' and ext not in supported_file_types:
                return f"Unsupported file type: {ext}"
            if kind == 'image' and ext not in supported_image_types:
                return f"Unsupported image type: {ext}"
            if kind == 'video' and ext not in supported_video_types:
                return f"Unsupported video type: {ext}"
            if f.size > max_file_size:
                mb_size = f.size / (1024 * 1024)
                return f"{kind.capitalize()} size exceeds 10MB. Size: {mb_size:.2f} MB"
            return None

        # Validate files
        for f in attrs.get("files", []):
            err = validate_file(f, "file")
            if err:
                errors.setdefault("files", []).append(err)

        # Validate images
        for img in attrs.get("images", []):
            err = validate_file(img, "image")
            if err:
                errors.setdefault("images", []).append(err)

        # Validate videos
        for vid in attrs.get("videos", []):
            err = validate_file(vid, "video")
            if err:
                errors.setdefault("videos", []).append(err)

        if errors:
            # Raise a ValidationError with all accumulated errors
            raise serializers.ValidationError(errors)

        return attrs

    def create(self, validated_data):
        """
        Bulk-create all Media objects after validation passes.
        """
        content_type_id = validated_data["content_type_id"]
        object_id = validated_data["object_id"]
        
        # Retrieve the ContentType
        try:
            ct = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"content_type_id": "Invalid content type ID."})
        
        new_media_objects = []

        # Prepare file-based media
        for f in validated_data.get("files", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="File", file=f)
            )

        for img in validated_data.get("images", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="Image", image=img)
            )

        for vid in validated_data.get("videos", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="Video", video=vid)
            )

        # Now do a single bulk_create
        Media.objects.bulk_create(new_media_objects)

        # Return the list of created objects
        return new_media_objects


