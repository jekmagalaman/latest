# apps/ai_service/views.py
import json
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages

from .models import AIReportSummary
from .utils import generate_ipmt_summary_sync, get_user_by_identifier
from apps.gso_reports.models import WorkAccomplishmentReport, IPMT, SuccessIndicator

# -------------------------------
# Role Checks
# -------------------------------
def is_gso_or_director(user):
    return user.is_authenticated and user.role in ["gso", "director"]


@login_required
@user_passes_test(is_gso_or_director)
def regenerate_ipmt_summary(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    data = json.loads(request.body)
    personnel = data.get("personnel")
    indicator = data.get("indicator")
    month = data.get("month")

    user = get_user_by_identifier(personnel)
    si = SuccessIndicator.objects.filter(code=indicator).first()

    ipmt_obj = IPMT.objects.filter(
        personnel=user,
        indicator=si,
        month=month
    ).first()

    if not ipmt_obj:
        return JsonResponse({"error": "IPMT not found"}, status=404)

    # Get linked WARs
    war_ids = [w.id for w in ipmt_obj.reports.all()]

    summary_dict = generate_ipmt_summary_sync(war_ids)
    new_summary = summary_dict.get(indicator, "")

    ipmt_obj.accomplishment = new_summary
    ipmt_obj.save(update_fields=["accomplishment"])

    return JsonResponse({"summary": new_summary})


@login_required
def ai_summary_list(request):
    """
    List all AI-generated summaries (for Director / GSO staff).
    """
    summaries = AIReportSummary.objects.select_related("report", "generated_by").all().order_by("-created_at")
    return render(request, "ai_service/ai_summary_list.html", {"summaries": summaries})


@login_required
def ai_summary_detail(request, report_id):
    """
    View AI-generated summaries for a specific Work Accomplishment Report (WAR).
    """
    report = get_object_or_404(WorkAccomplishmentReport, id=report_id)
    summaries = report.ai_summaries.all()
    return render(request, "ai_service/ai_summary_detail.html", {"report": report, "summaries": summaries})


@login_required
def generate_ai_summary(request, report_id):
    """
    Trigger synchronous generation of an AI summary for a WAR (Option B: no Celery).
    """
    report = get_object_or_404(WorkAccomplishmentReport, id=report_id)

    if request.method == "POST":
        ai_summary = generate_war_description_sync(report.id)
        if ai_summary:
            messages.success(request, f"AI summary generated for WAR #{report.id}.")
        else:
            messages.error(request, f"Failed to generate AI summary for WAR #{report.id}.")
        return redirect("ai_service:ai_summary_detail", report_id=report.id)

    return render(request, "ai_service/generate_ai_summary.html", {"report": report})


@login_required
def generate_ipmt_ai_summary(request, unit_name, month_filter):
    """
    Trigger synchronous generation of IPMT AI summaries for a unit+month.
    This view collects WAR ids for the requested unit/month, then calls the sync helper.
    """
    from apps.gso_reports.utils import collect_ipmt_reports

    try:
        year, month_num = map(int, month_filter.split("-"))
    except ValueError:
        messages.error(request, "Invalid month format. Use YYYY-MM.")
        return redirect("gso_reports:preview_ipmt")

    reports = collect_ipmt_reports(year, month_num, unit_name)

    if request.method == "POST":
        report_ids = [r["war_id"] for r in reports if r.get("war_id")]
        results = generate_ipmt_summary_sync(report_ids)

        # Optionally: persist or process `results` (mapping indicator -> remark).
        # For now we show a success message and redirect.
        messages.success(request, f"AI IPMT summaries generated for {unit_name} {month_filter}.")
        return redirect("gso_reports:preview_ipmt")

    return render(request, "ai_service/generate_ipmt_summary.html", {
        "unit_name": unit_name,
        "month_filter": month_filter,
        "reports": reports,
    })
