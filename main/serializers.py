from rest_framework import serializers
from profiles.models import AgentProfile
from .models import Media
from django.contrib.contenttypes.models import ContentType

import cloudinary.uploader
from .models import MessageMedia
from main.models import Media 



class AgentAssignmentSerializer(serializers.Serializer):
    """
    Serializer for assigning agents to homeowners by registration ID.
    
    ----------------------------
    INPUT PARAMETERS:
    - registration_id: str
    
    -----------------------------
    """
    registration_ID = serializers.CharField(max_length=100)




class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['id', 'content_type', 'object_id', 'media_type', 'image', 'image_category', 'file', 'video', 'upload_date']

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
    content_type_id = serializers.IntegerField()
    object_id = serializers.IntegerField()
    files = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        required=False
    )
    # Separate fields for before and after images
    before_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        required=False
    )
    after_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False),
        required=False
    )
    videos = serializers.ListField(
        child=serializers.FileField(allow_empty_file=False),
        required=False
    )

    def validate(self, attrs):
        max_file_size = 10 * 1024 * 1024
        supported_file_types = ['pdf', 'doc', 'docx', 'txt']
        supported_image_types = ['jpg', 'jpeg', 'png', 'gif']
        supported_video_types = ['mp4', 'avi', 'mov', 'mkv', 'ts']

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

        for f in attrs.get("files", []):
            err = validate_file(f, "file")
            if err:
                errors.setdefault("files", []).append(err)

        for img in attrs.get("before_images", []):
            err = validate_file(img, "image")
            if err:
                errors.setdefault("before_images", []).append(err)

        for img in attrs.get("after_images", []):
            err = validate_file(img, "image")
            if err:
                errors.setdefault("after_images", []).append(err)

        for vid in attrs.get("videos", []):
            err = validate_file(vid, "video")
            if err:
                errors.setdefault("videos", []).append(err)

        if errors:
            raise serializers.ValidationError(errors)
        return attrs

    def create(self, validated_data):
        content_type_id = validated_data["content_type_id"]
        object_id = validated_data["object_id"]

        try:
            ct = ContentType.objects.get(pk=content_type_id)
        except ContentType.DoesNotExist:
            raise serializers.ValidationError({"content_type_id": "Invalid content type ID."})

        new_media_objects = []

        for f in validated_data.get("files", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="File", file=f)
            )

        # Create Media for before images, defaulting their image category to 'before'
        for img in validated_data.get("before_images", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="Image", image=img, image_category="before")
            )

        # Create Media for after images, setting image_category to 'after'
        for img in validated_data.get("after_images", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="Image", image=img, image_category="after")
            )

        for vid in validated_data.get("videos", []):
            new_media_objects.append(
                Media(content_type=ct, object_id=object_id, media_type="Video", video=vid)
            )

        Media.objects.bulk_create(new_media_objects)
        return new_media_objects   
    
    

def upload_to_cloudinary(file):
    result = cloudinary.uploader.upload(file)
    return {
        "url": result["secure_url"],
        "public_id": result["public_id"],
        "media_type": result["resource_type"]
    }







class MessageMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageMedia
        fields = ["file_url", "public_id", "media_type"]

    def validate(self, attrs):
        if not attrs.get("media_type") or not attrs.get("file_url"):
            raise serializers.ValidationError("Both `media_type` and `file_url` are required.")

        if "cloudinary.com" not in attrs["file_url"]:
            raise serializers.ValidationError("Only Cloudinary URLs are supported.")

        return attrs

    def create(self, validated_data):
        message = self.context.get("message")
        if not message:
            raise serializers.ValidationError("Message instance is required.")
        return MessageMedia.objects.create(message=message, **validated_data)


