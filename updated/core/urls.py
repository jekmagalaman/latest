from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', lambda request: redirect('gso_accounts:login'), name='home'),
    path('admin/', admin.site.urls),


    path('gso_accounts/', include('apps.gso_accounts.urls', namespace='gso_accounts')),
    path('gso_requests/', include('apps.gso_requests.urls', namespace='gso_requests')),
    path('gso_inventory/', include('apps.gso_inventory.urls', namespace='gso_inventory')),
    path('gso_reports/', include('apps.gso_reports.urls', namespace='gso_reports')),
    path('ai/', include('apps.ai_service.urls', namespace='ai_service')),
    path('notifications/', include('apps.notifications.urls', namespace='notifications')),



    #lex
    # API URLs
    path('api/gso_accounts/', include('apps.gso_accounts.api.urls')),
    path('api/gso_requests/', include('apps.gso_requests.api.urls')),
    path('api/gso_inventory/', include('apps.gso_inventory.api.urls')),
    path('api/gso_reports/', include('apps.gso_reports.api.urls')),
    path('api/ai_service/', include('apps.ai_service.api.urls')),
    path('api/notifications/', include('apps.notifications.api.urls')),
    path('api/gso_migration/', include('apps.gso_migration.api.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)