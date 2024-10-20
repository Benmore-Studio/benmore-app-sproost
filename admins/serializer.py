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
        # Get the ID of the User instance being updated, if it exists
        user_id = self.instance.id if self.instance else None
        # Check if the email is already in use by another user
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use.')
        return email
    
    def update(self, instance, validated_data):
        print('home_owner', instance)

        # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.email = validated_data.get('email', instance.email) 
        instance.save()

        request_data = self.context['request'].data 
        

        # updating the nested contractor
        contractor_profile = ContractorProfile.objects.get(user=instance)

        contractor_profile.company_name = request_data.get('company_name', contractor_profile.company_name)
        contractor_profile.registration_number = request_data.get('registration_number', contractor_profile.registration_number)
        contractor_profile.specialization = request_data.get('specialization', contractor_profile.specialization)
        contractor_profile.company_address = request_data.get('company_address', contractor_profile.company_address)
        contractor_profile.website = request_data.get('website', contractor_profile.website)
        contractor_profile.city = request_data.get('city', contractor_profile.city)
        if 'image' in request_data:
            contractor_profile.image = request_data['image']
        
        contractor_profile.save()

        return instance
  
  
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

    def update(self, instance, validated_data):
        print('home_owner2', instance)
       # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.email = validated_data.get('email', instance.email) 
        instance.save()

        request_data = self.context['request'].data 
        

        # updating the nested contractor
        home_owner_profile = UserProfile.objects.get(user=instance)

        home_owner_profile.address = request_data.get('address', home_owner_profile.address)
        home_owner_profile.city = request_data.get('city', home_owner_profile.city)
        home_owner_profile.state_province = request_data.get('state_province', home_owner_profile.state_province)
        if 'image' in request_data:
            home_owner_profile.image = request_data['image']
        
        home_owner_profile.save()

        return instance


class UpdateAgentSerializer(serializers.ModelSerializer):
    """
    Serializer for User model, with nested AgentProfileSerializer.
    """
    # agent_profile = AgentProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','phone_number','user_type', 'last_name', 'agent_profile'] 

    def validate_email(self, value):
        email = value.lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise serializers.ValidationError('This email address is already in use.')
        return email

    def update(self, instance, validated_data):
        print('agent', instance)
        # Update User fields
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.user_type = validated_data.get('user_type', instance.user_type)
        instance.email = validated_data.get('email', instance.email) 
        instance.save()

        print('saved')
        request_data = self.context['request'].data 
        

        # updating the nested contractor
        agent_profile = AgentProfile.objects.get(user=instance)

        agent_profile.company_name = request_data.get('address', agent_profile.address)
        agent_profile.registration_ID = request_data.get('registration_ID', agent_profile.registration_ID)
        if 'image' in request_data:
            agent_profile.image = request_data['image']
        
        agent_profile.save()

        return instance
  