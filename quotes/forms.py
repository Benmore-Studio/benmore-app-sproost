from django import forms
from quotes.models import QuoteRequests

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
    

class QuoteRequestsForm(forms.ModelForm):

    class Meta:
        model = QuoteRequests
        fields = ["title", "summary", "contact_phone", "contact_email", "property_address"]

    def __init__(self, *args, **kwargs):
        super(QuoteRequestsForm, self).__init__(*args, **kwargs)

        common_attrs = {
            'class': 'w-full p-2 border border-gray-300 rounded-md focus:outline-none mt-1 focus:border-gray-500',
            'placeholder': 'Type here',
        }
        special_field_classes = {
            'summary': 'min-h-[120px]',
            'contact_email': "h-full outline-none group-focus:oouline-none"
        }

        for field_name, field in self.fields.items():
            field.widget.attrs.update(common_attrs)
            if field_name in special_field_classes:
                field.widget.attrs['class'] += f' {special_field_classes[field_name]}'

        self.fields['contact_phone'].widget.attrs.update({
            'class': 'w-10/12 rounded-md focus:outline-none mt-1 focus:border-gray-500',
            'placeholder': "+1 (555) 000-0000",
            'type': "tel"
        })

        self.fields['contact_email'].widget.attrs.update({
            'class': 'w-full h-full outline-none group-focus:outline-none mt-1 focus-visible:border-none border-none',
        })
