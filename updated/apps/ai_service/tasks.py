# apps/ai_service/tasks.py
from typing import List, Dict
from apps.gso_reports.models import WorkAccomplishmentReport
from .models import AIReportSummary
from .utils import query_local_ai, generate_ipmt_summary as utils_generate_ipmt_summary

def generate_war_description_sync(war_id: int) -> AIReportSummary | None:
    """
    Synchronous helper: generate an AI summary for a Work Accomplishment Report (WAR),
    save it to AIReportSummary and return the created instance (or None if not found).
    """
    try:
        war = WorkAccomplishmentReport.objects.get(id=war_id)
    except WorkAccomplishmentReport.DoesNotExist:
        return None

    # Build a compact prompt from the WAR fields (safe, minimal assumptions about model)
    war_desc = (war.description or "").strip() or "No description provided."
    activity = getattr(war, "activity_name", None) or getattr(war, "title", None) or "Work activity"
    unit_name = war.unit.name if getattr(war, "unit", None) else "General Services"

    prompt = (
        "You are an AI that generates short, professional government work logs.\n\n"
        f"Unit: {unit_name}\n"
        f"Activity: {activity}\n\n"
        f"WAR description:\n{war_desc}\n\n"
        "Write ONE concise sentence that summarizes the accomplishment clearly and factually. "
        "Do not include names or personnel, focus only on the task performed. "
        "Keep it formal, brief, and specific."
    )

    result = query_local_ai(prompt)

    ai_summary = AIReportSummary.objects.create(
        report=war,
        summary_text=result
    )

    return ai_summary


def generate_ipmt_summary_sync(report_ids: List[int]) -> Dict[str, str]:
    """
    Synchronous IPMT summary generator.

    - Accepts a list of WAR ids (report_ids).
    - Groups WARs by their success_indicator (best-effort using attribute names).
    - Calls utils.generate_ipmt_summary(success_indicator, war_descriptions) for each group.
    - Returns a dict mapping success_indicator -> generated remark.
    """
    wars = WorkAccomplishmentReport.objects.filter(id__in=report_ids)

    # Group descriptions by success indicator (use fallback "General" if not present)
    groups: Dict[str, List[str]] = {}
    for w in wars:
        # try common attribute names
        indicator = None
        for attr in ("success_indicator", "indicator", "indicator_code", "si_code"):
            if hasattr(w, attr):
                indicator = getattr(w, attr)
                break
        if not indicator:
            indicator = "General"

        desc = (w.description or "").strip()
        if not desc:
            continue

        groups.setdefault(str(indicator), []).append(desc)

    results: Dict[str, str] = {}
    for indicator, descriptions in groups.items():
        # Call the utility to create a concise summary for this indicator
        remark = utils_generate_ipmt_summary(indicator, descriptions)
        results[indicator] = remark

    return results
