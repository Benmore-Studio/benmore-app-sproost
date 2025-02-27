from rest_framework import serializers
from .models import Project
from quotes.models import QuoteRequest, QuoteRequestStatus, Property
from main.models import Media
from django.contrib.contenttypes.models import ContentType
from accounts.models import User
from profiles.models import ContractorProfile
 


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
        from django.contrib.contenttypes.models import ContentType
        from main.models import Media  # Adjust your import as needed

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




       
        
class PropertyCreateSerializer(serializers.ModelSerializer):
    before_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    after_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'property_owner', 'home_owner_agents', 
            'contractors', 'price', 'address', 'half_bath', 'full_bath', 'bathrooms', 
            'bedrooms', 'square_footage', 'total_square_foot', 'lot_size', 'scope_of_work', 
            'taxes', 'basement_details', 'garage', 'repair_recommendations', 'date_created',
            'likes', 'status', 'before_images', 'after_images'
        ]
        read_only_fields = ['id', 'date_created', 'likes', 'status']

    def create(self, validated_data):
        request = self.context.get("request")
        
          # Only allow users whose user_type is not "IV"
        if request and getattr(request.user, 'user_type', None) == 'IV':
            raise serializers.ValidationError(
                {"detail": "Investors are not allowed to create properties."}
            )
            
        if not validated_data.get('property_owner'):
            validated_data['property_owner'] = request.user
            
            
        # Extract media data from the request
        before_images = validated_data.pop('before_images', [])
        after_images = validated_data.pop('after_images', [])
                   
        # Extract many-to-many fields first.
        home_owner_agents = validated_data.pop('home_owner_agents', [])
        contractors = validated_data.pop('contractors', [])
        before_images = validated_data.pop('before_images', [])
        after_images = validated_data.pop('after_images', [])
        
        # Set the property owner automatically if not provided

        # Create the Property instance without M2M fields
        property_obj = Property.objects.create(**validated_data)
            

        # Create the Property. You may have additional logic to set the status.
        property_obj = super().create(validated_data)
        
        # Get ContentType for Property
        ct = ContentType.objects.get_for_model(Property)

        # Combine before and after images into one payload for BulkMediaSerializer.
        # (The BulkMediaSerializer expects keys: content_type_id, object_id, before_images, after_images.)
        media_payload = {
            "content_type_id": ct.id,
            "object_id": property_obj.id,
            "before_images": before_images,
            "after_images": after_images,
        }
        # Initialize and validate the bulk serializer.
        bulk_serializer = BulkMediaSerializer(data=media_payload, context=self.context)
        bulk_serializer.is_valid(raise_exception=True)
        # Save creates all Media objects.
        bulk_serializer.save()

        return property_obj
    
 
 
#  for property retrieval purposes, to fixed circular imports issues
class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
                'password': {'write_only': True},
                'last_login': {'read_only': True},
                'is_superuser': {'read_only': True},
            }


class SimpleContractorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = '__all__'     
    
class PropertyRetrieveSerializer(serializers.ModelSerializer):
    before_images = serializers.SerializerMethodField()
    after_images = serializers.SerializerMethodField()
    home_owner_agents = SimpleUserSerializer(many=True, read_only=True)
    contractors = SimpleContractorProfileSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'property_owner', 'home_owner_agents', 
            'contractors', 'price', 'address', 'half_bath', 'full_bath', 'bathrooms', 
            'bedrooms', 'square_footage', 'total_square_foot', 'lot_size', 'scope_of_work', 
          'garage', 'repair_recommendations', 'date_created',
            'likes', 'status', 'before_images', 'after_images'
        ]

    def get_before_images(self, obj):
        before_qs = obj.media_paths.filter(image_category="before")
        return MediaSerializer(before_qs, many=True, context=self.context).data

    def get_after_images(self, obj):
        after_qs = obj.media_paths.filter(image_category="after")
        return MediaSerializer(after_qs, many=True, context=self.context).data
    



class PropertyUpdateSerializer(serializers.ModelSerializer):
    # Optional fields for adding new images. These are write-only.
    before_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    after_images = serializers.ListField(
        child=serializers.ImageField(),
        required=False,
        write_only=True
    )
    
     # Many-to-many fields as primary key related fields
    home_owner_agents = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )
    contractors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ContractorProfile.objects.all(), required=False
    )
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'property_owner', 'home_owner_agents', 
            'contractors', 'price', 'address', 'half_bath', 'full_bath', 'bathrooms', 
            'bedrooms', 'square_footage', 'total_square_foot', 'lot_size', 'scope_of_work', 
          'garage', 'repair_recommendations', 'date_created',
            'likes', 'status', 'before_images', 'after_images'
        ]
        read_only_fields = ['property_owner', 'date_created', 'likes']
    
  
    def update(self, instance, validated_data):
        request = self.context.get("request")

        # Pop many-to-many and media fields.
        home_owner_agent_ids = validated_data.pop('home_owner_agents', None)
        contractor_ids = validated_data.pop('contractors', None)
        before_images = validated_data.pop('before_images', [])
        after_images = validated_data.pop('after_images', [])

        # Update regular fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # --- Update home_owner_agents ---
        if home_owner_agent_ids is not None and len(home_owner_agent_ids) > 0:
             # Retrieve users with the provided IDs, ensuring they have user_type 'AG'
            # and are not the property owner.
            valid_agents = User.objects.filter(
                id__in=home_owner_agent_ids,
                user_type='AG'
            ).exclude(id=instance.property_owner.id)
            if valid_agents.count() != len(home_owner_agent_ids):
                raise serializers.ValidationError({
                    "home_owner_agents": "One or more agent IDs are invalid, not of type AG, or belong to the property owner."
                })
            instance.home_owner_agents.set(valid_agents)
        else:
            # If not provided, and if the authenticated user qualifies, add them.
            request = self.context.get("request")
            if (request and getattr(request.user, 'user_type', None) == 'AG' and 
                request.user != instance.property_owner):
                instance.home_owner_agents.add(request.user)

        # --- Update contractors ---
        if contractor_ids is not None and len(contractor_ids) > 0:
            valid_contractors = ContractorProfile.objects.filter(
                id__in=contractor_ids
            ).select_related('user').exclude(user=instance.property_owner)
            valid_contractors = valid_contractors.filter(user__user_type='CO')
        
            if valid_contractors.count() != len(contractor_ids):
                raise serializers.ValidationError({
                    "contractors": "One or more contractor IDs are invalid, not of type CO, or belong to the property owner."
                })
            instance.contractors.set(valid_contractors)
        else:
            # If no contractor IDs are provided (or an empty list is provided),
            # and if the authenticated user qualifies as a contractor, add them.
            if (request and getattr(request.user, 'user_type', None) == 'CO' and 
                request.user != instance.property_owner):
                try:
                    # Use the correct attribute name for the contractor profile.
                    contractor_profile = request.user.contractor_profile  
                    instance.contractors.add(contractor_profile)
                except Exception as e:
                    raise serializers.ValidationError({"contractors": str(e)})
                
                
                # --- Process Media Uploads ---
        # Get the ContentType for the Property model.
        ct = ContentType.objects.get_for_model(Property)

        # Process new before images (just add new ones).
        if before_images:
            for image in before_images:
                Media.objects.create(
                    content_type=ct,
                    object_id=instance.id,
                    media_type="Image",
                    image=image,
                    image_category="before"
                )

        # Process new after images: remove old ones and add the new ones.
        if after_images:
            instance.media_paths.filter(image_category="after").delete()
            for image in after_images:
                Media.objects.create(
                    content_type=ct,
                    object_id=instance.id,
                    media_type="Image",
                    image=image,
                    image_category="after"
                )
            # Optionally update the status to 'completed'
            instance.status = "completed"
            
        instance.save()

        return instance