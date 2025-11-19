from rest_framework import permissions

class IsNotificationOwnerOrGSO(permissions.BasePermission):
    """
    Users can only access their own notifications, GSO Office or Director can access all.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role in ['gso', 'director']:
            return True
        return obj.user == request.user
