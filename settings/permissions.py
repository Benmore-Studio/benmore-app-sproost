# permissions.py
from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    """
    Custom permission to only allow access to admin users.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated and is an admin
        if request.user and request.user.is_staff:
            return True
        # Otherwise, deny access
        return False

    def message(self):
        # Custom error message
        return "You don't have the privilege to access this data or perform this action."
