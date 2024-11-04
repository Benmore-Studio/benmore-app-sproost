from django.contrib import admin
from .models import UserProfile, ContractorProfile, AgentProfile,Referral


admin.site.register(UserProfile)
admin.site.register(ContractorProfile)
admin.site.register(AgentProfile)
admin.site.register(Referral)