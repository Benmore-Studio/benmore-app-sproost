from django.shortcuts import render, redirect
from django.contrib.auth.models import AnonymousUser
from django.contrib import messages
from typing import Union, TypeVar


T = TypeVar("T")


# Create your views here.
class CustomRequestUtil:
    context: dict = None
    context_object_name = None
    template_name = None
    template_on_error = None

    def __init__(self, request):
        self.request = request
        self.permission_required = None

    @property
    def auth_user(self):
        user = self.request.user if self.request and self.request.user else None
        if isinstance(user, AnonymousUser):
            user = None

        return user

    def log_error(self, error):
        print(error)

    def make_error(self, message=None, error=None):
        if error:
            self.log_error(error)
        return message

    def process_request(self, request, target_view=None, target_function=None, **extra_args):
        if not self.context:
            self.context = dict()

        self.context['request'] = request

        if self.extra_context_data:
            for key, val in self.extra_context_data.items():
                self.context[key] = val

        response_raw_data = None

        if target_function:
            response_raw_data: Union[tuple, T] = target_function(**extra_args)

        return self.__handle_request_response(response_raw_data, target_view)

    def __handle_request_response(self, response_raw_data, target_view):
        response, error_detail = None, None

        if isinstance(response_raw_data, tuple):
            response, error_detail = response_raw_data
        else:
            response = response_raw_data

        if error_detail:
            messages.error(self.request, error_detail)
            if self.template_on_error:
                if isinstance(self.template_on_error, str):
                    return redirect(self.template_on_error)
                elif isinstance(self.template_on_error, tuple):
                    return redirect(self.template_on_error[0], self.template_on_error[1])
        else:
            if isinstance(response, str):
                messages.success(self.request, response)
            else:
                self.context[self.context_object_name] = response

        if self.template_name:
            return render(self.request, self.template_name, self.context)

        return redirect(target_view)
    

def user_type_required(user_types):
    ''' check if user is of a certain type '''
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type not in user_types:
                return redirect('main:home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
