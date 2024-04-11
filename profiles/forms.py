from django import forms
from .models import ContractorProfile, UserProfile

class ContractorProfileForm(forms.ModelForm):
    class Meta:
        model = ContractorProfile
        fields = ['company_name', 'registration_number', 'specialization', 'company_address', 'city']

class HomeOwnersEditForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [ 'address', 'city', 'state_province']
        # fields = "__all__"