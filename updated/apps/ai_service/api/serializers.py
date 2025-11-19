from rest_framework import serializers
from apps.ai_service.models import AIReportSummary

class AIReportSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = AIReportSummary
        fields = '__all__'

class AIReportSummaryCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIReportSummary
        fields = [
            'report',
            'summary_text',
            'generated_by'
        ]
