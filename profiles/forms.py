from django import forms
from .models import ContractorProfile, UserProfile
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from address.forms import AddressField, AddressWidget


class ContractorProfileForm(forms.ModelForm):
    # Defined phone_number and company_address fields as Django form fields
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    company_address = AddressField(
            required=False,
            widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )    
    email = forms.EmailField()
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'specialization', 'city', 'company_address', 'phone_number']


class HomeOwnersEditForm(forms.ModelForm):
    phone_number = PhoneNumberField()
    address = AddressField(
            required=False,
            widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )    
    class Meta:
        model = UserProfile
        fields = ['city', 'state_province', 'address']


        # fields = "__all__"