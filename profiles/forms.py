from django import forms

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import PhoneNumberPrefixWidget

from .models import ContractorProfile, UserProfile

class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'registration_number', 'specialization', 'company_address', 'city']

class HomeOwnersEditForm(forms.ModelForm):
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    class Meta:
        model = UserProfile
        fields = [ 'address', 'city', 'state_province', 'phone_number']
        # fields = "__all__"