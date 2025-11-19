from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceRequestViewSet, RequestMaterialViewSet, TaskReportViewSet, FeedbackViewSet

router = DefaultRouter()
router.register(r'service-requests', ServiceRequestViewSet, basename='service-request')
router.register(r'request-materials', RequestMaterialViewSet, basename='request-material')
router.register(r'task-reports', TaskReportViewSet, basename='task-report')
router.register(r'feedbacks', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]
