from rest_framework import permissions

class IsGSOAdmin(permissions.BasePermission):
    """
    Custom permission for GSO admins only.
    Only users with role 'gso' or 'director' can create/update/delete globally.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['gso', 'director']


class IsUnitHeadOrAdmin(permissions.BasePermission):
    """
    Unit heads can view and manage requests in their unit.
    GSO and Director can manage all.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['gso', 'director']:
            return True
        if request.user.role == 'unit_head':
            return obj.unit == request.user.unit
        return False


class IsAssignedPersonnelOrAdmin(permissions.BasePermission):
    """
    Personnel assigned to a request can view/update their own task reports.
    GSO and Director can manage all.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.role in ['gso', 'director']:
            return True
        if request.user.role == 'personnel':
            return request.user in obj.assigned_personnel.all()
        return False


class IsRequestorSelf(permissions.BasePermission):
    """
    Requestors can view their own requests.
    """

    def has_object_permission(self, request, view, obj):
        return obj.requestor == request.user
