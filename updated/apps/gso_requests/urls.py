from django.urls import path
from . import views

from apps.gso_inventory import views as inventory_views


app_name = "gso_requests"

urlpatterns = [
    # Director
    path('approve/<int:pk>/', views.approve_request, name='approve_request'),

    # GSO Office
    path('management/', views.request_management, name='request_management'),
    path('request/<int:pk>/update_indicator/', views.update_success_indicator, name='update_success_indicator'),


    # Unit Head
    path('unit-head/management/', views.unit_head_request_management, name='unit_head_request_management'),
    path('unit-head/detail/<int:pk>/', views.unit_head_request_detail, name='unit_head_request_detail'),
    path('unit-head/history/', views.unit_head_request_history, name='unit_head_request_history'),
    path("unit-head/inventory/", inventory_views.unit_head_inventory, name="unit_head_inventory"),

    path(
        "unit-head/inventory/<int:item_id>/",
        views.unit_head_material_detail,
        name="unit_head_material_detail",
    ),


    # Personnel
    path('personnel/tasks/', views.personnel_task_management, name='personnel_task_management'),
    path('personnel/task/<int:pk>/', views.personnel_task_detail, name='personnel_task_detail'),
    path('personnel/history/', views.personnel_history, name='personnel_history'),
    path('personnel/inventory/', views.personnel_inventory, name='personnel_inventory'),  # NEW

    # Requestor
    path('requestor/management/', views.requestor_request_management, name='requestor_request_management'),
    path('requestor/add/', views.add_request, name='add_request'),
    path('requestor/cancel/<int:pk>/', views.cancel_request, name='cancel_request'),
    path('requestor/history/', views.requestor_request_history, name='requestor_request_history'),

    # Feedback
    path('submit_feedback/', views.submit_feedback, name='submit_feedback'),

    #Motorpool
    path("requestor/motorpool/create/", views.add_motorpool_request, name="create_motorpool_request"),
    path("requestor/fuel-po/create/", views.create_fuel_po_request, name="create_fuel_po_request"),
]
