from django import forms
from address.forms import AddressField, AddressWidget
from .models import Property
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from phonenumber_field.formfields import PhoneNumberField

# class ProperyForm(forms.ModelForm):
#     address = AddressField(
#         required=False,
#         widget=AddressWidget(attrs={'placeholder': 'Enter Address', 'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500,placeholder=Enter Address'})
#     )
#     phone_number = PhoneNumberField(required=False, widget=PhoneNumberPrefixWidget(initial='US'))
#     class Meta:
#         model = Property
#         fields = ['name', 'address', 'phone_number', 'email']