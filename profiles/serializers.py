from rest_framework import serializers
from .models import ContractorProfile, UserProfile, AgentProfile
from accounts.models import User

class ContractorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContractorProfile
        fields = '__all__' 

class ContractorSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested ContractorProfile.
    """
    contractor_profile = ContractorProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'contractor_profile']  

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