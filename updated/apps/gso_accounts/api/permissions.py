from rest_framework.permissions import BasePermission

class IsGSOAdmin(BasePermission):
    """
    Only GSO Office users and superusers can manage accounts.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.role == 'gso' or request.user.is_superuser)
