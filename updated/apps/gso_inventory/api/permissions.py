from rest_framework import permissions

class IsGSOAdmin(permissions.BasePermission):
    """
    Only GSO office or Director can create/update/delete inventory items.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['gso', 'director']
