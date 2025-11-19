from rest_framework import permissions

class IsGSOorDirector(permissions.BasePermission):
    """
    Only GSO Office or Director can create or view all migrations.
    Other users have no access.
    """
    def has_permission(self, request, view):
        return request.user.role in ['gso', 'director']

    def has_object_permission(self, request, view, obj):
        return request.user.role in ['gso', 'director']
