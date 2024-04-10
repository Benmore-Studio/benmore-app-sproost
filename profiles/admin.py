from django.contrib import admin
from .models import UserProfile, ContractorProfile


admin.site.register(UserProfile)
admin.site.register(ContractorProfile)