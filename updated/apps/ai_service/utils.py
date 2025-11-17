# apps/ai_service/utils.py
import os
import requests
from typing import List, Dict
from django.contrib.auth import get_user_model
from apps.gso_requests.models import ServiceRequest, TaskReport  # ✅ Import models for richer prompts
from apps.gso_reports.models import WorkAccomplishmentReport

User = get_user_model()

# -------------------------------
# Local AI Model Config
# -------------------------------
AI_API_URL = os.getenv("AI_API_URL", "http://127.0.0.1:8001/v1/generate")
AI_API_KEY = os.getenv("AI_API_KEY", "mysecretkey")

# -------------------------------
# Query Local Private Model
# -------------------------------
def query_local_ai(prompt: str) -> str:
    """
    Send a prompt to the local private AI server (Flan-T5 model)
    and return the generated text.
    """
    try:
        response = requests.post(
            AI_API_URL,
            headers={
                "Content-Type": "application/json",
                "x-api-key": AI_API_KEY,
            },
            json={"prompt": prompt},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("result", "").strip()
    except Exception as e:
        return f"[AI Error] {e}"
    


def get_user_by_identifier(identifier: str):
    """
    Returns a User object based on identifier.
    Identifier can be username, email, or full name (simple search).
    Returns None if no match is found.
    """
    if not identifier:
        return None

    try:
        # Try username first
        return User.objects.get(username__iexact=identifier)
    except User.DoesNotExist:
        pass

    try:
        # Try email
        return User.objects.get(email__iexact=identifier)
    except User.DoesNotExist:
        pass

    # Optional: search by full name (first + last)
    qs = User.objects.filter(
        first_name__iexact=identifier.split(" ")[0],
        last_name__iexact=" ".join(identifier.split(" ")[1:]),
    )
    return qs.first() if qs.exists() else None


# -------------------------------
# Enhanced WAR Description Generator
# -------------------------------
def generate_war_description(request_obj: ServiceRequest) -> str:
    """
    Strict one-sentence WAR generator with no explanations,
    no meta commentary, and no hallucinations.
    """
    try:
        unit_name = request_obj.unit.name if request_obj.unit else "GSO Team"

        requestor_description = (
            request_obj.description.strip() if request_obj.description else "No description provided."
        )

        task_reports = TaskReport.objects.filter(request=request_obj)
        report_texts = [r.report_text.strip() for r in task_reports if r.report_text.strip()]
        reports_str = "\n".join([f"- {txt}" for txt in report_texts]) or "No personnel reports available."

        prompt = (
            "You generate Work Accomplishment Report (WAR) statements.\n"
            "STRICT OUTPUT MODE:\n"
            "- Output ONLY ONE sentence.\n"
            "- DO NOT provide explanations.\n"
            "- DO NOT restate the instructions.\n"
            "- DO NOT add any commentary.\n"
            "- DO NOT include quotes.\n"
            "- DO NOT add context, assumptions, or invented details.\n"
            "- Use ONLY the information provided.\n"
            "- Write from the perspective of the unit performing the task.\n"
            "- No pronouns like our/my/their.\n"
            "- No mentioning names.\n\n"
            f"Unit: {unit_name}\n"
            f"Request description: {requestor_description}\n"
            f"Personnel reports: {reports_str}\n\n"
            "Now produce the ONE SENTENCE accomplishment statement:"
        )

        return query_local_ai(prompt).strip()

    except Exception as e:
        return f"[AI Error] Failed to generate WAR: {e}"

# -------------------------------
# IPMT Summary Generator (Improved)
# -------------------------------
def generate_ipmt_summary_sync(report_ids: List[int]) -> Dict[str, str]:
    """
    Synchronous IPMT summary generator.

    - Accepts a list of WAR ids (report_ids).
    - Groups WARs by their success_indicator.
    - Calls the local AI to summarize all descriptions per indicator.
    - Returns a dict mapping success_indicator -> generated remark.
    """
    wars = WorkAccomplishmentReport.objects.filter(id__in=report_ids)

    # Group descriptions by success indicator (use fallback "General" if not present)
    groups: Dict[str, List[str]] = {}
    for w in wars:
        indicator = w.success_indicator.code if w.success_indicator else "General"
        desc = (w.description or "").strip()
        if not desc:
            continue
        groups.setdefault(indicator, []).append(desc)

    results: Dict[str, str] = {}
    for indicator, descriptions in groups.items():
        if not descriptions:
            results[indicator] = f"No accomplishments recorded for indicator: {indicator}."
            continue

        # Build prompt for AI to write concise, unit-focused sentence
        activities_text = "\n".join([f"- {desc}" for desc in descriptions])
        prompt = (
            f"Summarize the following work accomplishments for the success indicator '{indicator}':\n\n"
            f"{activities_text}\n\n"
            "Write ONE concise sentence describing what the assigned personnel/unit did. "
            "Do NOT mention requestors. "
            "Do NOT include names. "
            "Use active voice and formal government style. "
            "Keep it clear, specific, and professional."
        )

        remark = query_local_ai(prompt).strip()
        results[indicator] = remark

    return results