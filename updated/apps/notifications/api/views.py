from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.notifications.models import Notification
from .serializers import NotificationSerializer, NotificationCreateUpdateSerializer
from .permissions import IsNotificationOwnerOrGSO

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    permission_classes = [IsAuthenticated, IsNotificationOwnerOrGSO]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return NotificationCreateUpdateSerializer
        return NotificationSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role in ['gso', 'director']:
            return Notification.objects.all()
        return Notification.objects.filter(user=user)
