from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import View

from accounts.models import UserTypes
from services.utils import CustomRequestUtil

# Create your views here.

loggedInUser = 'contractor'

class Quotes(View, CustomRequestUtil):
    template_name = "user/request_quotes.html"
    extra_context_data = {}

    def get(self, request, *args, **kwargs):
        self.extra_context_data = {
            'loggedInUser': f"{UserTypes.contractor}"
        }
        
        return self.process_request(request)


def requestQuotes(request):
    context ={
        'loggedInUser': loggedInUser
    }
    return render(request, 'user/request_quotes.html', context)