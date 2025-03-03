import json
from rest_framework import serializers
from .models import AssignedAccount, Property
from accounts.models import User
from profiles.models import ContractorProfile
from django.contrib.contenttypes.models import ContentType
from main.models import Media
from quotes.serializers import MediaSerializer, BulkMediaSerializer
from .models import AssignedAccount, Property
from accounts.models import User
from profiles.models import ContractorProfile
from django.contrib.contenttypes.models import ContentType
from main.models import Media
from quotes.serializers import MediaSerializer, BulkMediaSerializer

class AssignedAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedAccount
        fields = '__all__'
 
 
 
 
      
        
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
    
    # Write-only field for updating contractor IDs.
    contractors = serializers.PrimaryKeyRelatedField(
        many=True, queryset=ContractorProfile.objects.all(), required=False, write_only=True
    )
    # Read-only field for nested contractor profile details.
     
    # Many-to-many field for home_owner_agents remains unchanged.
    home_owner_agents = serializers.PrimaryKeyRelatedField(
        many=True, queryset=User.objects.all(), required=False
    )
    
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'property_type', 'property_owner', 'home_owner_agents', 
            'contractors',   # Include both fields
            'price', 'address', 'half_bath', 'full_bath', 'bathrooms', 
            'bedrooms', 'square_footage', 'total_square_foot', 'lot_size', 'scope_of_work', 
            'garage', 'repair_recommendations', 'date_created',
            'likes', 'status', 'before_images', 'after_images'
        ]
        read_only_fields = ['property_owner', 'date_created', 'likes']
        
    def to_internal_value(self, data):
        """
        Parse any JSON-like strings into actual Python lists before DRF validates them.
        """
        if hasattr(data, 'copy'):
            data = data.copy()

        # Parse 'contractors' if provided as a JSON string.
        contractors_str = data.get('contractors')
        if isinstance(contractors_str, str):
            try:
                data['contractors'] = json.loads(contractors_str)
            except json.JSONDecodeError:
                raise serializers.ValidationError({
                    'contractors': 'Expected a JSON array, e.g. [1,2].'
                })

        # Parse 'home_owner_agents' if provided as a JSON string.
        agents_str = data.get('home_owner_agents')
        if isinstance(agents_str, str):
            try:
                data['home_owner_agents'] = json.loads(agents_str)
            except json.JSONDecodeError:
                raise serializers.ValidationError({
                    'home_owner_agents': 'Expected a JSON array, e.g. [1,2].'
                })

        return super().to_internal_value(data)
    
    def update(self, instance, validated_data):
        request = self.context.get("request")

        # Pop many-to-many and media fields.
        home_owner_agent_data = validated_data.pop('home_owner_agents', None)
        contractor_data = validated_data.pop('contractors', None)
        before_images = validated_data.pop('before_images', None)
        after_images = validated_data.pop('after_images', None)

        # Update regular fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
    # TODO: CHECK BACK ON THIS IN THE FUTURE UPDATES
        # --- Update home_owner_agents ---
        if home_owner_agent_data is not None and len(home_owner_agent_data) > 0:
            # Ensure we are working with IDs.
            agent_ids = [agent.id if hasattr(agent, 'id') else agent for agent in home_owner_agent_data]
            valid_agents = User.objects.filter(
                id__in=agent_ids,
                user_type='AG'
            ).exclude(id=instance.property_owner.id)
            if valid_agents.count() != len(agent_ids):
                raise serializers.ValidationError({
                    "home_owner_agents": "One or more agent IDs are invalid, not of type AG, or belong to the property owner."
                })
            instance.home_owner_agents.set(valid_agents)
        else:
            # If not provided, and if the authenticated user qualifies, add them.
            if (request and getattr(request.user, 'user_type', None) == 'AG' and 
                request.user != instance.property_owner):
                instance.home_owner_agents.add(request.user)

        # --- Update contractors ---
        if contractor_data is not None and len(contractor_data) > 0:
            contractor_ids = [contractor.id if hasattr(contractor, 'id') else contractor for contractor in contractor_data]
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