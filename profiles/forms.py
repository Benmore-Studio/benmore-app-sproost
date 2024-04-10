from django import forms
from .models import ContractorProfile

class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'registration_number', 'specialization', 'company_address', 'city']
