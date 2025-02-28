from django.contrib import admin
from .models import AssignedAccount, Property

admin.site.register([AssignedAccount, Property])
 