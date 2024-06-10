from django.contrib import admin
from .models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'user_type', 'phone_number')}),
        (('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'slug'),
        }),
        (('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'slug', 'is_staff', 'phone_number', 'user_type')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'slug')
    ordering = ('username',)

admin.site.register(User, UserAdmin)