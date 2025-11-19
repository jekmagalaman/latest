from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UnitViewSet, DepartmentViewSet,
    PositionViewSet, EmploymentStatusViewSet
)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'units', UnitViewSet)
router.register(r'departments', DepartmentViewSet)
router.register(r'positions', PositionViewSet)
router.register(r'employment-status', EmploymentStatusViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
