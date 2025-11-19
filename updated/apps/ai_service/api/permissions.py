from rest_framework import permissions

class IsGSOOrAIUser(permissions.BasePermission):
    """
    Only GSO Office, Director, or the AI generator user can create/update AI summaries.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['gso', 'director', 'unit_head']
