from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.gso_inventory.models import InventoryItem
from .serializers import InventoryItemSerializer, InventoryItemCreateUpdateSerializer
from .permissions import IsGSOAdmin

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    permission_classes = [IsAuthenticated, IsGSOAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return InventoryItemCreateUpdateSerializer
        return InventoryItemSerializer
