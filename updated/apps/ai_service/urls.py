# apps/ai_service/urls.py
from django.urls import path
from . import views

app_name = "ai_service"

urlpatterns = [
    # Work Accomplishment Report (WAR) AI Summaries
    path("summaries/", views.ai_summary_list, name="ai_summary_list"),
    path("summaries/<int:report_id>/", views.ai_summary_detail, name="ai_summary_detail"),
    path("summaries/<int:report_id>/generate/", views.generate_ai_summary, name="generate_ai_summary"),

    # IPMT AI Summaries — pass unit_name and month_filter in the URL
    # Example: /ai_service/ipmt/generate/UnitName/2025-10/
    path("ipmt/generate/<str:unit_name>/<str:month_filter>/", views.generate_ipmt_ai_summary, name="generate_ipmt_ai_summary"),

    path("regenerate_ipmt_summary/", views.regenerate_ipmt_summary, name="regenerate_ipmt_summary"),
]
