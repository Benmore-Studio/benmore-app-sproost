
from allauth.account.forms import SignupForm
from phonenumber_field.formfields import PhoneNumberField
from django import forms
from .models import UserProfile
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django.contrib import messages


class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone_number = PhoneNumberField( widget=PhoneNumberPrefixWidget(initial='US'))
    address = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Enter home address'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Select City'}))
    state = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Select State'}))
    user_type = forms.ChoiceField(choices=UserProfile.USER_TYPE_CHOICES, widget=forms.RadioSelect)
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.save()
        UserProfile.objects.create(
            user = user,
            phone_number = self.cleaned_data['phone_number'],
            home_address = self.cleaned_data['address'],
            city = self.cleaned_data['city'],
            state = self.cleaned_data['state'],
            user_type = self.cleaned_data['user_type']
        )
        messages.success(request, 'Account created successfully')
        return user