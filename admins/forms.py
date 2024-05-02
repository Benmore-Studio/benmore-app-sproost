from django import forms
from quotes.models import QuoteRequestStatus

class QuoteStatusForm(forms.Form):
    status = forms.ChoiceField(choices=QuoteRequestStatus.choices, required=True)
    