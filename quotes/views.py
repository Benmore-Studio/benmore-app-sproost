from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View
from django.contrib import messages

from accounts.models import UserTypes, User
from accounts.services.user import UserService
from quotes.forms import QuoteRequestForm
from quotes.services import QuoteService
from services.utils import CustomRequestUtil


class Quotes(LoginRequiredMixin, View, CustomRequestUtil):
    template_name = "user/request_quotes.html"
    extra_context_data = {}
    form_class = QuoteRequestForm

    def get_initial_data(self):
        if self.user.user_type == 'HO':
            return {
                'contact_username': self.user.username,
                'contact_phone': self.user.phone_number,
                'property_address': self.user.user_profile.address,
                'custom_home_owner_id': self.request.user.pk,
                'created_by_agent': self.request.user.pk
            }
        elif self.user.user_type == 'AG':
            return {
                'contact_username': self.user.username,
                'contact_phone': self.user.phone_number,
                'property_address': self.user.agent_profile.address
            }

    def get(self, request, *args, **kwargs):
        home_owner_id = kwargs.get("id")
        self.user = self.auth_user

        if home_owner_id:
            user_service = UserService(request)
            self.user, error = user_service.fetch_single_by_pk(id=home_owner_id)

            if error:
                messages.error(request, error)
                return redirect('main:home')
        
        initial_data = self.get_initial_data()
        form = self.form_class(initial=initial_data)
        self.extra_context_data = {
            "loggedInUser": f"{UserTypes.contractor}",
            "form": form
        }
        
        return self.process_request(request)
    
    def post(self, request, *args, **kwargs):
        self.user = self.auth_user
        home_owner_id = kwargs.get("name")
        self.template_name = None
        initial_data = self.get_initial_data()
        form = self.form_class(request.POST, request.FILES)

        if home_owner_id:
            self.template_on_error = ("quotes:request-quotes", home_owner_id)
        else:
            self.template_on_error = "quotes:request-quotes"

        if form.is_valid():
            form_data = form.cleaned_data

            # if home_owner_id:
            #     user = User.objects.get(slug=home_owner_id)
            #     form_data["created_by_agent"] = request.user
            #     form_data["user"] = user
            # else:
            #     form_data["user"] = request.user
            #     form_data["created_by_agent"] = None

            form_data["user"] = request.user
            form_data['media'] = None
            if request.FILES:
                uploaded_files = request.FILES.getlist("media")
                form_data["media"] = uploaded_files
            
            print(request.FILES)
            print(request.POST)
            print('form_data')
            quote_service = QuoteService(request)
            return self.process_request(request, target_view="main:home", target_function=quote_service.create, payload=form_data)

        else:
            self.extra_context_data["form"] = form
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(self.request, f"{error}")
            form = self.form_class(initial=initial_data, data=request.POST)
            return render(request, 'user/request_quotes.html', {'form': form})




