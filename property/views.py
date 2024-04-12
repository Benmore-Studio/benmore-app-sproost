from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView
from .models import Property
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from quotes.models import Project
from django.contrib.auth.decorators import login_required
from . import forms

class PropertyListView(ListView):
    model = Property
    template_name = 'property/propertyList.html'
    context_object_name = 'properties'
    
    def get_queryset(self):
        return Property.objects.all().order_by('-id')


# class AddProperty(LoginRequiredMixin, CreateView):
#     form_class = forms.ProperyForm
#     template_name = 'property/add_property.html'
#     success_url = reverse_lazy('property:property-list')
    
#     def form_valid(self, form):
#         messages.success(self.request, "Property added successfully")
#         return super().form_valid(form)

@login_required
def add_property_by_uuid(request):
    if request.method == 'POST':
        form = forms.AddPropertyByUUIDForm(request.POST)
        if form.is_valid():
            uuid = form.cleaned_data['uuid']
            try:
                project = Project.objects.get(quote_request__uuid=uuid)
                if Property.objects.filter(project=project).exists():
                    messages.error(request, 'Property already added')
                    return redirect('main:home')
                
                Property.objects.create(
                    assigned_by = project.quote_request.user, #TODO cross check who the person is
                    assigned_to = request.user, 
                    project = project, 
                    is_approved = True,
                )
                messages.success(request, 'Property Added Successfully')
            except Project.DoesNotExist:
                messages.error(request, 'Project not found')
            return redirect('main:home')