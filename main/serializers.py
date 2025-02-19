from rest_framework import serializers
from profiles.models import AgentProfile
from .models import Media
from django.contrib.contenttypes.models import ContentType


class AgentAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning agents to homeowners by registration ID.
    
    ----------------------------
    INPUT PARAMETERS:
    - registration_id: str
    
    -----------------------------
    """
    registration_ID = serializers.CharField(max_length=100)


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



class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            'id',
            'file_url',
            'public_id',
            'media_type',
            'image',
            'file',
            'video',
            'upload_date',
        ]
