from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages

from accounts.models import UserTypes
from accounts.services.user import UserService
from quotes.forms import QuoteRequestForm
from quotes.services import QuoteService
from services.utils import CustomRequestUtil


class Quotes(LoginRequiredMixin, View, CustomRequestUtil):
    template_name = "user/request_quotes.html"
    extra_context_data = {}
    form_class = QuoteRequestForm

    def get(self, request, *args, **kwargs):
        home_owner_id = kwargs.get("id")

        self.user = self.auth_user

        if home_owner_id:
            user_service = UserService(request)
            self.user, error = user_service.fetch_single_by_pk(id=home_owner_id)

            if error:
                messages.error(request, error)
                return redirect('main:home')

        form = self.form_class(initial={
            'contact_email': self.user.email,
            'contact_phone': self.user.phone_number,
            'property_address': self.user.user_profile.address
        })

        self.extra_context_data = {
            "loggedInUser": f"{UserTypes.contractor}",
            "form": form
        }
        
        return self.process_request(request)
    

    def post(self, request, *args, **kwargs):
        home_owner_id = kwargs.get("id")

        if home_owner_id:
            self.template_on_error = ("quotes:request-quotes", home_owner_id)
        else:
            self.template_on_error = "quotes:request-quotes"

        self.template_name = None
        
        form = self.form_class(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            form_data["home_owner_id"] = home_owner_id
            form_data['media'] = None

            if request.FILES:
                uploaded_files = request.FILES.getlist("upload-quote")
                uploaded_captures = request.FILES.getlist("upload-capture")

                print(uploaded_captures, uploaded_files)

                form_data["media"] = uploaded_files + uploaded_captures
                print("form_data: ", form_data['media'])

            quote_service = QuoteService(request)

            return self.process_request(request, target_view="main:home", target_function=quote_service.create, payload=form_data)

        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{error}")

            return redirect('quotes:request-quotes')
