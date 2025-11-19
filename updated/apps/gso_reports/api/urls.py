from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SuccessIndicatorViewSet, WorkAccomplishmentReportViewSet, IPMTViewSet

router = DefaultRouter()
router.register(r'success-indicators', SuccessIndicatorViewSet, basename='successindicator')
router.register(r'war', WorkAccomplishmentReportViewSet, basename='war')
router.register(r'ipmt', IPMTViewSet, basename='ipmt')

urlpatterns = [
    path('', include(router.urls)),
]
