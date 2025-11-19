from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.ai_service.models import AIReportSummary
from .serializers import AIReportSummarySerializer, AIReportSummaryCreateUpdateSerializer
from .permissions import IsGSOOrAIUser

class AIReportSummaryViewSet(viewsets.ModelViewSet):
    queryset = AIReportSummary.objects.all()
    permission_classes = [IsAuthenticated, IsGSOOrAIUser]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return AIReportSummaryCreateUpdateSerializer
        return AIReportSummarySerializer
