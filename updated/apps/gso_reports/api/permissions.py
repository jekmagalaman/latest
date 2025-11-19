from rest_framework import permissions

class IsGSOAdmin(permissions.BasePermission):
    """
    Only GSO Office or Director can create/update/delete reports.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['gso', 'director']
