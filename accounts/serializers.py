from rest_framework import serializers
from django.contrib.auth import get_user_model
from profiles.models import UserProfile, AgentProfile, ContractorProfile, Referral, InvestorProfile
from property.models import AssignedAccount
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.serializerfields import PhoneNumberField



User = get_user_model()

class CustomSignupSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    phone_number = PhoneNumberField(required=False) 

    home_owner_address = serializers.CharField(required=False)
    city = serializers.CharField(max_length=100, required=False)
    state = serializers.CharField(max_length=100, required=False)
    user_type = serializers.ChoiceField(choices=[('HO', 'Home Owner'), ('AG', 'Agent'), ('CO', 'Contractor'), ('IV', 'Investor')], required=True)
    referral_code = serializers.CharField(max_length=100, required=False)


    # Contractor Info
    company_name = serializers.CharField(max_length=255, required=False)
    specialization = serializers.CharField(max_length=225, required=False)
    company_address = serializers.CharField(max_length=255, required=False)
    country= serializers.CharField(max_length=225, required=False)
    insurance_number = serializers.CharField(max_length=255, required=False)
    license_number= serializers.CharField(max_length=225, required=False)

    # Agent Info
    registration_ID= serializers.CharField(help_text='registration_ID', max_length=225, required=False)
    agent_address = serializers.CharField(max_length=255, required=False)


    # investor info
    investor_company_name = serializers.CharField(max_length=255, required=False)
    investor_specialization = serializers.CharField(max_length=225, required=False)
    investor_company_address = serializers.CharField(max_length=255, required=False)
    investor_country= serializers.CharField(max_length=225, required=False)
    image= serializers.ImageField(required=False)

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone_number', 'home_owner_address', 'city', 'state', 'user_type',
            'referral_code', 'company_name', 'specialization', 'company_address',
            'registration_ID',  'insurance_number', 'license_number', 'country','agent_address', 'email', 'password', 'image',
            'investor_company_name','investor_specialization','investor_company_address','investor_country'
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


    def validate(self, data):
        # Retrieve the fields for cross-validation
        user_type = data.get('user_type')
        email = data.get('email')
        phone_number = data.get('phone_number', None) 
        home_owner_address = data.get('home_owner_address', None) 
        
        if not phone_number:
            raise serializers.ValidationError({"phone_number": "Phone Number is required."})

        # Validate email field globally
        if not email:
            raise serializers.ValidationError({"email": "This field is required."})

        if user_type == "HO":
            if not home_owner_address:
                raise serializers.ValidationError({"home_owner_address": "Home Address required."})
        
        # Validate registration_ID based on user_type
        if user_type == 'AG':
            Real_estate_license = data.get('registration_ID', None) 
            brokerage_address = data.get('agent_address', None) 

            if not Real_estate_license:
                raise serializers.ValidationError({"Real_estate_license": "Real Estate License is required for Agents."})
            if not brokerage_address:
                raise serializers.ValidationError({"brokerage_address": "brokerage Address is required for Agents."})
            if AgentProfile.objects.filter(registration_ID=Real_estate_license).exists():
                raise serializers.ValidationError({"registration_ID": "An agent with this registration ID already exists."})
            
        if user_type == 'CO':
            insurance_number = data.get('insurance_number', None) 
            license_number = data.get('license_number', None) 
            company_name = data.get('company_name', None) 
            company_address = data.get('company_address', None) 
            specialization = data.get('specialization', None) 
            image = data.get('image', None) 
            if not insurance_number:
                raise serializers.ValidationError({"insurance_number": "Insurance Number is required for Contractors."})
            if not company_name:
                raise serializers.ValidationError({"company_name": "Company Name is required for Contractors."})
            if not company_address:
                raise serializers.ValidationError({"company_address": "Company Address is required for Contractors."})
            if not license_number:
                raise serializers.ValidationError({"license_number": "License Number is required for Contractors."})
            if not specialization:
                raise serializers.ValidationError({"specialization": "Specialization is required for Contractors."})
            if not image:
                raise serializers.ValidationError({"image": "image is required for Contractors."})
            if ContractorProfile.objects.filter(license_number=license_number).exists():
                raise serializers.ValidationError({"license_number": "A Contractor with this License ID already exists."})
        
        if user_type == 'IV':
            investor_company_name = data.get('investor_company_name', None) 
            investor_company_address = data.get('investor_company_address', None) 
            investor_specialization = data.get('investor_specialization', None) 
            investor_country = data.get('investor_country', None) 
            if not investor_company_name:
                raise serializers.ValidationError({"investor_company_name": "Company Name is required for Contractors."})
            if not investor_company_address:
                raise serializers.ValidationError({"investor_company_address": "Company Address is required for Contractors."})
            if not investor_specialization:
                raise serializers.ValidationError({"investor_specialization": "Specialization is required for Contractors."})
            if not investor_country:
                raise serializers.ValidationError({"investor_country": "Country is required for Contractors."})
            
        return data


    # def validate_registration_ID(self, value):
    #     user_type = self.initial_data.get('user_type')
    #     email = self.initial_data.get('email')
    #     if user_type == 'AG' and not value:
    #         raise serializers.ValidationError("Registration ID is required for Agents.")
    #     if AgentProfile.objects.filter(registration_ID=value).exists():
    #         raise serializers.ValidationError("An agent with this registration ID already exists.")
    #     if not email:
    #         raise serializers.ValidationError({"email": "This field is required."})
    #     return value


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
                home_owner_address=validated_data.get('address')
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
                agent_address=validated_data.get('agent_address'),
                registration_ID=validated_data.get('registration_ID'),
            )

        elif user.user_type == "CO":
            ContractorProfile.objects.create(
                user=user,
                company_name=validated_data.get('company_name'),
                specialization=validated_data.get('specialization'),
                company_address=validated_data.get('company_address'),
                country=validated_data.get('country'),
                license_number=validated_data.get('license_number'),
                insurance_number=validated_data.get('insurance_number'),
                image=validated_data.get('image'),
            )

        elif user.user_type == "IV":
            InvestorProfile.objects.create(
                user=user,
                company_name=validated_data.get('investor_company_name'),
                specialization=validated_data.get('investor_specialization'),
                company_address=validated_data.get('investor_company_address'),
                country=validated_data.get('investor_country'),
            )

        return user



class GoogleSignUpSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=5000, required=True)


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=6)