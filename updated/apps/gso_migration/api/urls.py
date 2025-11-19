from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MigrationUploadViewSet

router = DefaultRouter()
router.register(r'migrations', MigrationUploadViewSet, basename='migration')

urlpatterns = [
    path('', include(router.urls)),
]
