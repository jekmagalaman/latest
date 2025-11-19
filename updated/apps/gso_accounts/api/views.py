from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    UserSerializer, UserCreateUpdateSerializer,
    UnitSerializer, DepartmentSerializer,
    PositionSerializer, EmploymentStatusSerializer
)
from ..models import User, Unit, Department, Position, EmploymentStatus
from .permissions import IsGSOAdmin

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsGSOAdmin]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserSerializer

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]

class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]

class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]

class EmploymentStatusViewSet(viewsets.ModelViewSet):
    queryset = EmploymentStatus.objects.all()
    serializer_class = EmploymentStatusSerializer
    permission_classes = [IsAuthenticated, IsGSOAdmin]
