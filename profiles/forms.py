from django import forms
from .models import ContractorProfile, UserProfile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from address.forms import AddressField, AddressWidget
from django.contrib.auth import get_user_model

User = get_user_model()

class ContractorProfileForm(forms.ModelForm):
    # Defined phone_number and company_address fields as Django form fields
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    company_address = AddressField(
            widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )    
    email = forms.EmailField()
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'specialization', 'city', 'registration_number',  'company_address', 'phone_number']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user object from kwargs
        super().__init__(*args, **kwargs)
        if user:
            user_profile = ContractorProfile.objects.get(user=user)
            # Set default values for the fields based on the user's profile
            self.fields['company_address'].initial = user_profile.company_address
            self.fields['phone_number'].initial = user_profile.user.phone_number

    def clean_email(self):
        email = self.cleaned_data.get('email')
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class HomeOwnersEditForm(forms.ModelForm):
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    address = AddressField(
            widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )    
    email = forms.EmailField()
    class Meta:
        model = UserProfile
        fields = ['city', 'state_province', 'address', 'phone_number', 'email']


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Extract the user object from kwargs
        super().__init__(*args, **kwargs)
        if user:
            user_profile = UserProfile.objects.get(user=user)
            # Set default values for the fields based on the user's profile
            self.fields['address'].initial = user_profile.address
            self.fields['phone_number'].initial = user_profile.user.phone_number

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     user_id = self.instance.user.id if self.instance.user else None
    #     if User.objects.exclude(id=user_id).filter(email=email).exists():
    #         raise forms.ValidationError('This email address is already in use.')
    #     return email