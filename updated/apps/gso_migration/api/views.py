from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from apps.gso_migration.models import MigrationUpload
from .serializers import MigrationUploadSerializer, MigrationUploadCreateUpdateSerializer
from .permissions import IsGSOorDirector

class MigrationUploadViewSet(viewsets.ModelViewSet):
    queryset = MigrationUpload.objects.all()
    permission_classes = [IsAuthenticated, IsGSOorDirector]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MigrationUploadCreateUpdateSerializer
        return MigrationUploadSerializer

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
