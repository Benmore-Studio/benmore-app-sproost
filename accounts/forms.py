# forms.py
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from .models import USER_TYPE_CHOICES
from profiles.models import UserProfile, ContractorProfile, AgentProfile, Referral
from property.models import AssignedAccount
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib import messages
from address.forms import AddressField, AddressWidget
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site



from mail_templated import send_mail





def get_base_url(request):
    # Use 'get_current_site' to get the domain
    domain = get_current_site(request).domain
    # Use 'request.is_secure' to determine the scheme (http or https)
    scheme = 'https' if request.is_secure() else 'http'
    # Construct the base URL
    base_url = f"{scheme}://{domain}"
    return base_url

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30,required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
    address = AddressField(
        required=False,
        widget=AddressWidget(attrs={'placeholder': 'Enter address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
    )
    city = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Select city'}))
    state = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': 'Select state'}))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, widget=forms.RadioSelect)
    referral_code = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput())

    # Contractor Info
    company_name = forms.CharField(max_length=255, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter company name'}))
    specialization = forms.CharField(max_length=225, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter specialization'}))
    company_address = AddressField(
        required=False,
        widget=AddressWidget(attrs={'placeholder': 'Enter address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
    )

    # Agent Info
    registration_ID = forms.CharField(max_length=225, required=False, widget=forms.TextInput(attrs={'placeholder': 'Enter registration number'}))
    agent_first_name = forms.CharField(max_length=30, required=False, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    agent_last_name = forms.CharField(max_length=30,required=False, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    agent_address = AddressField(
        required=False,
        widget=AddressWidget(attrs={'placeholder': 'Enter address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500'})
    )

    def clean_registration_ID(self):
        registration_ID = self.cleaned_data['registration_ID']
        user_type = self.cleaned_data['user_type']
        if not registration_ID and user_type == 'AG':
            raise forms.ValidationError('Registration ID is required')
        return registration_ID

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.user_type = self.cleaned_data['user_type']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()

        if user.user_type == "HO":
            UserProfile.objects.create(
                user = user,
                address = self.cleaned_data['address']
            ) 
            
            # Handle referral code directly from the request
            referral_code = request.GET.get('ref', '')
            if referral_code:
                try:
                    referral = Referral.objects.get(code=referral_code)
                    referral.referred.add(user)
                    referral.save()
                    try:                          
                        agent = AgentProfile.objects.get(registration_ID=referral_code)
                        if AssignedAccount.objects.filter(assigned_by=user, assigned_to=agent.user).exists():
                            pass
                        else:
                            AssignedAccount.objects.get_or_create(
                                assigned_to=agent.user,
                                assigned_by=user,
                                is_approved=True
                            )
                            send_mail(
                                'mail/assign_agent.tpl',
                                {'first_name': agent.user.first_name, "base_url": get_base_url(request)},
                                settings.EMAIL_HOST_USER,
                                [agent.user.email]
                            )

                    except AgentProfile.DoesNotExist:
                        pass
                except Referral.DoesNotExist:
                    pass   

        elif user.user_type == "AG": 
            user.first_name = self.cleaned_data['agent_first_name']
            user.last_name = self.cleaned_data['agent_last_name']
            user.save()        
            AgentProfile.objects.create(
                user = user,
                address = self.cleaned_data['agent_address'],
                registration_ID = self.cleaned_data['registration_ID'],
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
    