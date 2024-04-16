
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from .models import USER_TYPE_CHOICES
from profiles.models import UserProfile, ContractorProfile
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib import messages
from address.forms import AddressField, AddressWidget
        
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30,required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    address = AddressField(
        required=False,
        widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
    )
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Select City'}))
    state = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Select State'}))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter Company Name'}))
    registration_number = forms.CharField(max_length=225, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter Registration Number'}))
    specialization = forms.CharField(max_length=225, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter Specialization'}))
    company_address = AddressField(
        required=False,
        widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
    )
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        
        if user.user_type != "CO":
            UserProfile.objects.create(
                user = user,
                address = self.cleaned_data['address'],
                city = self.cleaned_data['city'],
                state_province = self.cleaned_data['state'],
            )
        else:
            ContractorProfile.objects.create(
                user = user, 
                company_name = self.cleaned_data['company_name'],
                specialization = self.cleaned_data['specialization'],
                company_address = self.cleaned_data['company_address'],
                city = self.cleaned_data['city'],
            )

        messages.success(request, 'Account created successfully')
        return user
    

class ValidatePhoneNumberForm(forms.Form):
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    