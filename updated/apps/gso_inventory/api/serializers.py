from rest_framework import serializers
from apps.gso_inventory.models import InventoryItem

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'


class InventoryItemCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = [
            'name',
            'description',
            'quantity',
            'unit_of_measurement',
            'category',
            'owned_by',
            'is_active',
        ]
