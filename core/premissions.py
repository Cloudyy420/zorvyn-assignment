from rest_framework.permissions import BasePermission
from apps.users.models import Role

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role == Role.ADMIN)

class IsAnalystOrAbove(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.role in (Role.ANALYST, Role.ADMIN))

class IsActiveUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated
                    and request.user.is_active)

class IsOwnerOrAdmin(BasePermission):
    """Object-level permission: edit/delete only own records or if admin."""
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user or request.user.role == Role.ADMIN

class CanModifyRecord(IsAnalystOrAbove):
    """Analyst+ can modify records. Ownership enforced at object level."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == Role.ADMIN:
            return True
        return obj.created_by == request.user