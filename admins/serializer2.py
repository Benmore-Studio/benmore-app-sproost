from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from profiles.models import ContractorProfile,AgentProfile, UserProfile
from accounts.models import User
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth import get_user_model
from address.models import Address
from profiles.serializers import ContractorProfileSerializer, HomeOwnerProfileSerializer, AgentProfileSerializer


User = get_user_model()


class UpdateContractorProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested ContractorProfile.
    """
    contractor_profile = ContractorProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'contractor_profile']  

    def validate_email(self, value):
        email = value.lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use.')
        return email
    

class UpdateHomeOwnerSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested HomeOwnerProfileSerializer.
    """
    user_profile = UserProfile()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'user_profile'] 

    def validate_email(self, value):
        email = value.lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use.')
        return email


class UpdateAgentSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested AgentProfileSerializer.
    """
    agent_profile = AgentProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'agent_profile'] 

    def validate_email(self, value):
        email = value.lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use.')
        return email
