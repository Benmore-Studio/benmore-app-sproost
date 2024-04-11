from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Property
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from . import forms

class PropertyListView(ListView):
    model = Property
    template_name = 'property/propertyList.html'
    context_object_name = 'properties'
    
    def get_queryset(self):
        return Property.objects.all().order_by('-id')


class AddProperty(LoginRequiredMixin, CreateView):
    form_class = forms.ProperyForm
    template_name = 'property/add_property.html'
    success_url = reverse_lazy('property:property-list')
    
    def form_valid(self, form):
        messages.success(self.request, "Property added successfully")
        return super().form_valid(form)
