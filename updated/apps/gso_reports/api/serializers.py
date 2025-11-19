from rest_framework import serializers
from apps.gso_reports.models import SuccessIndicator, WorkAccomplishmentReport, IPMT

class SuccessIndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessIndicator
        fields = '__all__'

class WorkAccomplishmentReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAccomplishmentReport
        fields = '__all__'

class WorkAccomplishmentReportCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAccomplishmentReport
        fields = [
            'request',
            'unit',
            'assigned_personnel',
            'requesting_office_name',
            'personnel_names',
            'date_started',
            'date_completed',
            'activity_name',
            'description',
            'success_indicator',
            'status',
            'material_cost',
            'labor_cost',
            'total_cost',
            'control_number'
        ]

class IPMTSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPMT
        fields = '__all__'

class IPMTCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPMT
        fields = [
            'personnel',
            'unit',
            'month',
            'indicator',
            'accomplishment',
            'remarks',
            'reports'
        ]
