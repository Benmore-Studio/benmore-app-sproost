from rest_framework import serializers
from .models import ContractorProfile, UserProfile, AgentProfile
from main.serializers import MediaSerializer
from accounts.models import User
from quotes.serializers import  QuoteRequestAllSerializer
from quotes.models import Property, QuoteRequest
from rest_framework.exceptions import APIException



class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'phone_number','user_type', 'last_name', 'agent_profile', 'date_joined'] 


class SimpleContractorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = '__all__' 


class SimpleHomeOwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__' 

class SimplePropertySerializer(serializers.ModelSerializer):
    media_paths = MediaSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = '__all__' 


class SimpleAgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProfile
        fields = '__all__' 


class PropertySerializer(serializers.ModelSerializer):
    home_owner_invited_agents = SimpleUserSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = '__all__'


class ContractorUserSerializer(serializers.ModelSerializer):
    contractor_profile = SimpleContractorProfileSerializer(read_only=True)
    property_owner = PropertySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'last_name', 'first_name',
            'username',
            'phone_number',
            'user_type',
            'email',
            'contractor_profile',
            'property_owner',
        ]


class ContractorSerializer(serializers.ModelSerializer):
    contractor_profile = SimpleContractorProfileSerializer(read_only=True)
    property_owner = PropertySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'id',
            'phone_number',
            'user_type',
            'username',
            'email',
            'contractor_profile',
            'property_owner',
        ]


class HomeOwnerSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested HomeOwnerProfileSerializer.
    """
    user_profile = SimpleHomeOwnerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type',  'last_name', 'user_profile'] 



class AgentUserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested AgentProfileSerializer.
    """
    user = SimpleUserSerializer()

    class Meta:
        model = AgentProfile
        fields = [ 'user', 'agent_address','registration_ID','image', 'country'] 

class AgentSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested AgentProfileSerializer.
    """
    agent_profile = SimpleAgentProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'agent_profile'] 


class ProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = ['image']

    def validate_image(self, value):
        if not value:
            raise None
        return value

#region userprofiles manytomany section

class UserProfileManyToManySerializer(serializers.ModelSerializer):
    home_owner_invited_agents = SimpleUserSerializer(many=True, read_only=True)
    home_owner_associated_contarctors = SimpleUserSerializer(many=True, read_only=True)
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'home_owner_address',
            'city',
            'state_province',
            'image',
            'user',
            'home_owner_invited_agents',
            'home_owner_associated_contarctors',
        ]


 
# for getUserRelatedOtherProfiles views
class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileManyToManySerializer(read_only=True)
    property_owner = PropertySerializer(many=True, read_only=True)
    quote_requests = QuoteRequestAllSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'last_name', 'phone_number',
            'user_type', 'first_name', 'email',"user_profile", 'property_owner', 'quote_requests']



class HomeViewUserSerializer(serializers.ModelSerializer):
    # using a method field for `user_profile`
    user_profile = serializers.SerializerMethodField()
    
    property_owner = SimplePropertySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'phone_number',
            'user_type', 'email', 'last_name', 'first_name', 'user_type', 'user_profile', 'property_owner']
    
    def get_user_profile(self, user):
        """
        Returns a nested serializer based on user.user_type
        """
        if user.user_type == "HO":
            # For homeowners
            return SimpleHomeOwnerProfileSerializer(user.user_profile).data
        
        elif user.user_type == "AG":
            # For agents
            return SimpleAgentProfileSerializer(user.agent_profile).data
        
        elif user.user_type == "CO":
            # For contractors
            return SimpleContractorProfileSerializer(user.contractor_profile).data
        
        # Default case (maybe None or an empty dict)
        return None

class QuotePropertySerializer(serializers.ModelSerializer):
    property = SimplePropertySerializer(read_only=True)

    class Meta:
        model = QuoteRequest
        fields =  fields = ['id', 'property']

class PolymorphicUserSerializer(serializers.Serializer):
    """
    A serializer that, for each User instance, picks the right sub-serializer
    based on user_type, but doesnt include property, unlike the previous polymorphic serializers.
    """

    def to_representation(self, instance):
        if instance.user_type == 'HO':
            return HomeOwnerSerializer(instance, context=self.context).data
        elif instance.user_type == 'AG':
            return AgentSerializer(instance, context=self.context).data
        elif instance.user_type == 'CO':
            return ContractorSerializer(instance, context=self.context).data
        else:
            # Instead of returning a BasicUserSerializer, raise an exception:
            raise APIException("Unauthorized user type.")


#endregion

