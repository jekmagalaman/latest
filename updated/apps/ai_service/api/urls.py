from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AIReportSummaryViewSet

router = DefaultRouter()
router.register(r'ai-summaries', AIReportSummaryViewSet, basename='ai-summary')

urlpatterns = [
    path('', include(router.urls)),
]
