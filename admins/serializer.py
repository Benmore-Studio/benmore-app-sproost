from rest_framework import serializers
from accounts.models import User
from profiles.models import ContractorProfile, AgentProfile, UserProfile
from profiles.serializers import (
    ContractorProfileSerializer,
    HomeOwnerProfileSerializer,
    AgentProfileSerializer
)

class BaseProfileSerializer(serializers.ModelSerializer):
    """
    Base serializer for updating User model and associated profile data.
    """

    def validate_email(self, value):
        email = value.lower()
        user_id = self.instance.id if self.instance else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use.')
        return email

    def update_user_fields(self, instance, validated_data):
        """
        Update fields common to the User model.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.email = validated_data.get('email', instance.email)
        instance.save()
        return instance

    def update_profile_fields(self, profile_instance, profile_data, profile_fields):
        """
        Generic method to update profile fields.
        """
        for field in profile_fields:
            setattr(profile_instance, field, profile_data.get(field, getattr(profile_instance, field)))
        profile_instance.save()
        return profile_instance


class UpdateContractorProfileSerializer(BaseProfileSerializer):
    contractor_profile = ContractorProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'phone_number', 'user_type', 'last_name', 'contractor_profile']

    def update(self, instance, validated_data):
        # Update user fields
        instance = self.update_user_fields(instance, validated_data)

        # Update contractor profile fields
        contractor_profile = instance.contractor_profile
        contractor_data = self.context['request'].data
        profile_fields = ['company_name', 'registration_number', 'specialization', 'company_address', 'website', 'city', 'image']
        self.update_profile_fields(contractor_profile, contractor_data, profile_fields)

        return instance


class UpdateHomeOwnerSerializer(BaseProfileSerializer):
    user_profile = HomeOwnerProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'phone_number', 'user_type', 'last_name', 'user_profile']

    def update(self, instance, validated_data):
        # Update user fields
        instance = self.update_user_fields(instance, validated_data)

        # Update homeowner profile fields
        home_owner_profile = instance.user_profile
        home_owner_data = self.context['request'].data
        profile_fields = ['address', 'city', 'state_province', 'image']
        self.update_profile_fields(home_owner_profile, home_owner_data, profile_fields)

        return instance


class UpdateAgentSerializer(BaseProfileSerializer):
    agent_profile = AgentProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'phone_number', 'user_type', 'last_name', 'agent_profile']

    def update(self, instance, validated_data):
        # Update user fields
        instance = self.update_user_fields(instance, validated_data)

        # Update agent profile fields
        agent_profile = instance.agent_profile
        agent_data = self.context['request'].data
        profile_fields = ['registration_ID', 'address', 'image'] 
        self.update_profile_fields(agent_profile, agent_data, profile_fields)

        return instance
