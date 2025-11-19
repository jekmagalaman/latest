from rest_framework import serializers
from ..models import ServiceRequest, RequestMaterial, TaskReport, Feedback
from apps.gso_accounts.api.serializers import UserSerializer
from apps.gso_inventory.api.serializers import InventoryItemSerializer
from apps.gso_reports.api.serializers import SuccessIndicatorSerializer

class RequestMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestMaterial
        fields = '__all__'

class TaskReportSerializer(serializers.ModelSerializer):
    personnel = UserSerializer(read_only=True)

    class Meta:
        model = TaskReport
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Feedback
        fields = '__all__'

class ServiceRequestSerializer(serializers.ModelSerializer):
    requestor = UserSerializer(read_only=True)
    assigned_personnel = UserSerializer(many=True, read_only=True)
    materials = InventoryItemSerializer(many=True, read_only=True)
    selected_indicator = SuccessIndicatorSerializer(read_only=True)

    class Meta:
        model = ServiceRequest
        fields = '__all__'

class ServiceRequestCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequest
        fields = '__all__'
