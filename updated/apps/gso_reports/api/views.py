from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.gso_reports.models import SuccessIndicator, WorkAccomplishmentReport, IPMT
from .serializers import (
    SuccessIndicatorSerializer,
    WorkAccomplishmentReportSerializer,
    WorkAccomplishmentReportCreateUpdateSerializer,
    IPMTSerializer,
    IPMTCreateUpdateSerializer
)
from .permissions import IsGSOAdmin

class SuccessIndicatorViewSet(viewsets.ModelViewSet):
    queryset = SuccessIndicator.objects.all()
    permission_classes = [IsAuthenticated, IsGSOAdmin]
    serializer_class = SuccessIndicatorSerializer

class WorkAccomplishmentReportViewSet(viewsets.ModelViewSet):
    queryset = WorkAccomplishmentReport.objects.all()
    permission_classes = [IsAuthenticated, IsGSOAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return WorkAccomplishmentReportCreateUpdateSerializer
        return WorkAccomplishmentReportSerializer

class IPMTViewSet(viewsets.ModelViewSet):
    queryset = IPMT.objects.all()
    permission_classes = [IsAuthenticated, IsGSOAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return IPMTCreateUpdateSerializer
        return IPMTSerializer
