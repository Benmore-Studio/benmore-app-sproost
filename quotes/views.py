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
        print(self.user.user_type)

        if home_owner_id:
            user_service = UserService(request)
            self.user, error = user_service.fetch_single_by_pk(id=home_owner_id)

            if error:
                messages.error(request, error)
                return redirect('main:home')
            
        if self.user.user_type == 'HO':
            print(request.user.pk)
            form = self.form_class(initial={
                'contact_email': self.user.email,
                'contact_phone': self.user.phone_number,
                'property_address': self.user.user_profile.address,
                'custom_home_owner_id': request.user.pk,
                'created_by_agent': request.user.pk
            })
        elif self.user.user_type == 'AG':
            form = self.form_class(initial={
                'contact_email': self.user.email,
                'contact_phone': self.user.phone_number,
                'property_address': self.user.agent_profile.address
            })

        self.extra_context_data = {
            "loggedInUser": f"{UserTypes.contractor}",
            "form": form
        }
        
        return self.process_request(request)
    

    def post(self, request, *args, **kwargs):
        # home_owner_id is also home_owner_name but not renamed
        home_owner_id = kwargs.get("name")
        print(home_owner_id)

        if home_owner_id:
            self.template_on_error = ("quotes:request-quotes", home_owner_id)
        else:
            self.template_on_error = "quotes:request-quotes"

        self.template_name = None
        
        form = self.form_class(request.POST)
        # print(request.POST)

        if form.is_valid():
            form_data = form.cleaned_data

            if form_data['custom_home_owner_id']:
                form_data["created_by_agent"] = request.user

            # form_data["home_owner_id"] = home_owner_id
            form_data['media'] = None

            print('form_data')
            print(form_data)

            if request.FILES:
                uploaded_files = request.FILES.getlist("upload-quote")
                uploaded_captures = request.FILES.getlist("upload-capture")

                form_data["media"] = uploaded_files + uploaded_captures
            quote_service = QuoteService(request)
            print(quote_service)

            return self.process_request(request, target_view="main:home", target_function=quote_service.create, payload=form_data)

        else:
            print(form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{error}")

            return redirect('quotes:confirm-request-quotes')
