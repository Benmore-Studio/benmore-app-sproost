from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import UserProfile, AgentProfile, ContractorProfile, Referral
from property.models import AssignedAccount
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.serializerfields import PhoneNumberField



User = get_user_model()

class CustomSignupSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    phone_number = PhoneNumberField(required=False)  # Use this for input validation

    address = serializers.CharField(required=False)
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    user_type = serializers.ChoiceField(choices=[('HO', 'Home Owner'), ('AG', 'Agent'), ('CO', 'Contractor')])
    referral_code = serializers.CharField(max_length=100, required=False)

    # Contractor Info
    company_name = serializers.CharField(max_length=255, required=False)
    specialization = serializers.CharField(max_length=225, required=False)
    company_address = serializers.CharField(max_length=255, required=False)

    # Agent Info
    registration_ID = serializers.CharField(max_length=225, required=False)
    agent_first_name = serializers.CharField(max_length=30, required=False)
    agent_last_name = serializers.CharField(max_length=30, required=False)
    agent_address = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'address', 'city', 'state', 'user_type',
            'referral_code', 'company_name', 'specialization', 'company_address',
            'registration_ID', 'agent_first_name', 'agent_last_name', 'agent_address', 'email', 'password'
        ]

        extra_kwargs = {
            'password': {'write_only': True},  # Ensures 'password' is only used for writing, not for reading
        }


    def to_representation(self, instance):
        """
        Convert phone number to string format during serialization.
        """
        representation = super().to_representation(instance)
        # Ensure phone_number is serialized as a string (E.164 format)
        representation.pop('password', None)  # Remove password from the response
        if instance.phone_number:
            representation['phone_number'] = str(instance.phone_number)
        return representation

    def validate_registration_ID(self, value):
        user_type = self.initial_data.get('user_type')
        email = self.initial_data.get('email')
        if user_type == 'AG' and not value:
            raise serializers.ValidationError("Registration ID is required for Agents.")
        if AgentProfile.objects.filter(registration_ID=value).exists():
            raise serializers.ValidationError("An agent with this registration ID already exists.")
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})
        return value

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("This field is required.")
        return value

    def create(self, validated_data):
        username = validated_data.get('email')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("A user with this Email already exists.")
        user = User.objects.create(
            username=username,
            email=username,
            first_name=validated_data.get('first_name'),
            last_name=validated_data.get('last_name'),
        )
        user.set_password(validated_data.get('password'))
        user.user_type = validated_data.get('user_type')
        user.phone_number = validated_data.get('phone_number')
        user.save()

        if user.user_type == "HO":
            UserProfile.objects.create(
                user=user,
                address=validated_data.get('address')
            )
            referral_code = validated_data.get('referral_code')
            if referral_code:
                try:
                    referral = Referral.objects.get(code=referral_code)
                    referral.referred.add(user)
                    referral.save()

                    # Handle agent assignment if referral code is agent's registration ID
                    agent = AgentProfile.objects.get(registration_ID=referral_code)
                    AssignedAccount.objects.get_or_create(
                        assigned_to=agent.user,
                        assigned_by=user,
                        is_approved=True
                    )
                except (Referral.DoesNotExist, AgentProfile.DoesNotExist):
                    pass

        elif user.user_type == "AG":
            AgentProfile.objects.create(
                user=user,
                address=validated_data.get('agent_address'),
                registration_ID=validated_data.get('registration_ID'),
            )

        elif user.user_type == "CO":
            ContractorProfile.objects.create(
                user=user,
                company_name=validated_data.get('company_name'),
                specialization=validated_data.get('specialization'),
                company_address=validated_data.get('company_address'),
                city=validated_data.get('city'),
            )

        return user


class GoogleSignUpSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=500, required=True)


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)
