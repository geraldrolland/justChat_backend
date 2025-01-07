from rest_framework.permissions import BasePermission

class IsStaffPermission(BasePermission):
    def has_permission(self, request, view):
        pass
    
class IsAdminPermission(BasePermission):
    def has_permission(self, request, view):
        pass