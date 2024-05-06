from django import forms    



class AgentAssignmentForm(forms.Form):
    registration_id = forms.CharField(max_length=100)