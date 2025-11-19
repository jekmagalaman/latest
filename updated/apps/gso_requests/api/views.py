from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from ..models import ServiceRequest, RequestMaterial, TaskReport, Feedback
from .serializers import (
    ServiceRequestSerializer, ServiceRequestCreateUpdateSerializer,
    RequestMaterialSerializer, TaskReportSerializer, FeedbackSerializer
)
from .permissions import IsGSOAdmin  # reuse the same permission class

class ServiceRequestViewSet(viewsets.ModelViewSet):
    queryset = ServiceRequest.objects.all()
    permission_classes = [IsAuthenticated, IsGSOAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ServiceRequestCreateUpdateSerializer
        return ServiceRequestSerializer

class RequestMaterialViewSet(viewsets.ModelViewSet):
    queryset = RequestMaterial.objects.all()
    serializer_class = RequestMaterialSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]

class TaskReportViewSet(viewsets.ModelViewSet):
    queryset = TaskReport.objects.all()
    serializer_class = TaskReportSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]
