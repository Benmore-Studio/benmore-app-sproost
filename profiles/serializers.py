from rest_framework import serializers
from .models import ContractorProfile, UserProfile, AgentProfile
from quotes.models import Property
from accounts.models import User
from quotes.serializers import  QuoteRequestAllSerializer


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class ContractorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = '__all__' 

class PropertySerializer(serializers.ModelSerializer):
    home_owner_invited_agents = SimpleUserSerializer(many=True, read_only=True)
    class Meta:
        model = Property
        fields = '__all__'

class ContractorSerializer(serializers.ModelSerializer):
    contractor_profile = ContractorProfileSerializer(read_only=True)
    property_owner = PropertySerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'contractor_profile',
            'property_owner',
        ]



class HomeOwnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__' 


class HomeOwnerSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested HomeOwnerProfileSerializer.
    """
    user_profile = HomeOwnerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'user_profile'] 


class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProfile
        fields = '__all__' 


class AgentSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested AgentProfileSerializer.
    """
    agent_profile = AgentProfileSerializer()

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



 

class UserSerializer(serializers.ModelSerializer):
    user_profile = UserProfileManyToManySerializer(read_only=True)
    property_owner = PropertySerializer(many=True, read_only=True)
    quote_requests = QuoteRequestAllSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email',"user_profile", 'property_owner', 'quote_requests']
#endregion

