from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages

from accounts.models import UserTypes
from quotes.forms import QuoteRequestsForm
from quotes.services import QuoteService
from services.utils import CustomRequestUtil


class Quotes(LoginRequiredMixin, View, CustomRequestUtil):
    template_name = "user/request_quotes.html"
    extra_context_data = {}
    form_class = QuoteRequestsForm

    def get(self, request, *args, **kwargs):
        self.extra_context_data = {
            "loggedInUser": f"{UserTypes.contractor}",
            "form": self.form_class
        }
        
        return self.process_request(request)
    

    def post(self, request, *args, **kwargs):
        self.template_on_error = "quotes:request-quotes"
        self.template_name = None
        
        form = self.form_class(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            if request.FILES:
                uploaded_files = request.FILES.getlist("upload-quote")
                form_data["media"] = uploaded_files

            quote_service = QuoteService(request)

            return self.process_request(request, target_view="main:home", target_function=quote_service.create, payload=form_data)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{error}")

            return redirect('quotes:request-quotes')
