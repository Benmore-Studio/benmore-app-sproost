from django import forms
from profiles.models import AgentProfile, ContractorProfile, UserProfile
from quotes.models import QuoteRequestStatus
from address.forms import AddressField, AddressWidget
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth import get_user_model

User = get_user_model()

class QuoteStatusForm(forms.Form):
    status = forms.ChoiceField(choices=QuoteRequestStatus.choices, required=True)

class UpdateContractorProfileForm(forms.ModelForm):
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    company_address = AddressField(
            widget=AddressWidget(attrs={'placeholder': 'Company Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )  
    email = forms.EmailField()
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'specialization', 'company_address', 'email', 'phone_number']
        
        
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email

class UpdateHomeOwnerForm(forms.ModelForm):
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    address = AddressField(
            widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )    
    email = forms.EmailField()
    class Meta:
        model = UserProfile
        fields = ['city', 'state_province', 'address', 'phone_number', 'email']


    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    
class UpdateAgentForm(forms.ModelForm):
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    address = AddressField(
            widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
        )    
    email = forms.EmailField()
    class Meta:
        model = AgentProfile
        fields = ['address', 'phone_number', 'email', 'registration_ID' ]
    
    def clean_email(self):
        email = self.cleaned_data.get('email').lower()
        user_id = self.instance.user.id if self.instance.user else None
        if User.objects.exclude(id=user_id).filter(email=email).exists():
            raise forms.ValidationError('This email address is already in use.')
        return email
    

