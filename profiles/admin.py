from django.contrib import admin
from .models import UserProfile, ContractorProfile, AgentProfile,Invitation


admin.site.register(UserProfile)
admin.site.register(ContractorProfile)
admin.site.register(AgentProfile)
admin.site.register(Invitation)