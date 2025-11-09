# apps/gso_requests/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponseForbidden

from .models import ServiceRequest, RequestMaterial, Unit, TaskReport
from apps.gso_accounts.models import User
from apps.gso_inventory.models import InventoryItem
from .utils import filter_requests, get_unit_inventory, create_war_from_request
from apps.gso_reports.models import WorkAccomplishmentReport, SuccessIndicator


# -------------------------------
# Role checks
# -------------------------------
def is_gso(user): return user.is_authenticated and user.role == "gso"
def is_unit_head(user): return user.is_authenticated and user.role == "unit_head"
def is_requestor(user): return user.is_authenticated and user.role == "requestor"
def is_director(user): return user.is_authenticated and user.role == "director"


# -------------------------------
# GSO Office Views
# -------------------------------
@login_required
@user_passes_test(is_gso)
def request_management(request):
    requests_qs = ServiceRequest.objects.select_related("requestor", "unit").prefetch_related("assigned_personnel").order_by("-created_at")

    # Apply filters
    requests_qs = filter_requests(
        requests_qs,
        search_query=request.GET.get("q"),
        unit_filter=request.GET.get("unit"),
    )

    units = Unit.objects.all()
    return render(request, "gso_office/request_management/request_management.html", {
        "requests": requests_qs,
        "units": units,
        "search_query": request.GET.get("q"),
        "unit_filter": request.GET.get("unit"),
    })


# -------------------------------
# Director Views
# -------------------------------
@login_required
@user_passes_test(is_director)
def director_request_management(request):
    requests_qs = ServiceRequest.objects.select_related("requestor", "unit").prefetch_related("assigned_personnel").order_by("-created_at")

    # Apply filters
    requests_qs = filter_requests(
        requests_qs,
        search_query=request.GET.get("q"),
        unit_filter=request.GET.get("unit"),
    )

    units = Unit.objects.all()
    return render(request, "director/director_request_management.html", {
        "requests": requests_qs,
        "units": units,
        "search_query": request.GET.get("q"),
        "unit_filter": request.GET.get("unit"),
    })


@login_required
@user_passes_test(is_director)
def approve_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk)
    if req.status != "Pending":
        return HttpResponseForbidden("This request cannot be approved.")

    req.status = "Approved"
    req.save()
    return redirect("gso_requests:director_request_management")


# -------------------------------
# Unit Head Views
# -------------------------------
@login_required
@user_passes_test(is_unit_head)
def unit_head_request_management(request):
    requests_qs = ServiceRequest.objects.filter(
        unit=request.user.unit
    ).exclude(status__in=["Completed", "Cancelled"]).order_by("-created_at")

    # Apply filters
    requests_qs = filter_requests(
        requests_qs,
        search_query=request.GET.get("q"),
        status_filter=request.GET.get("status"),
    )

    return render(request, "unit_heads/unit_head_request_management/unit_head_request_management.html", {
        "requests": requests_qs
    })

@login_required
@user_passes_test(is_unit_head)
def unit_head_request_detail(request, pk):
    service_request = get_object_or_404(ServiceRequest, pk=pk)

    # --- Identify Busy Personnel (assigned to active requests) ---
    busy_personnel = User.objects.filter(
        assigned_requests__status__in=["Pending", "Approved", "In Progress"]
    ).distinct()

    # --- Available Personnel (same unit, active, not busy) ---
    available_personnel = User.objects.filter(
        role="personnel",
        unit=service_request.unit,
        is_active=True
    ).exclude(id__in=busy_personnel).order_by("id")

    # --- You can still fetch all personnel for optional display ---
    all_personnel = User.objects.filter(
        role="personnel",
        unit=service_request.unit,
        is_active=True
    ).order_by("id")

    # --- Materials for the same unit ---
    materials = InventoryItem.objects.filter(
        is_active=True,
        owned_by=service_request.unit
    ).order_by("id")

    # --- Progress Reports ---
    reports = service_request.reports.select_related("personnel").order_by("-created_at")

    # --- Linked WAR (if already created) ---
    war = getattr(service_request, "war", None)

    # --- All available success indicators for that unit ---
    indicators = SuccessIndicator.objects.filter(
        unit=service_request.unit,
        is_active=True
    ).order_by("code")

    # --- Handle Form Submissions ---
    if request.method == "POST":
        action = request.POST.get("action")

        # === Save/Update Success Indicator ===
        if "save_success_indicator" in request.POST:
            si_id = request.POST.get("success_indicator")
            if si_id:
                si = get_object_or_404(SuccessIndicator, id=si_id, unit=service_request.unit)
                service_request.selected_indicator = si
                service_request.save(update_fields=["selected_indicator"])
                messages.success(request, "✅ Success Indicator updated for this request.")
            else:
                messages.warning(request, "⚠️ Please select a valid Success Indicator.")
            return redirect("gso_requests:unit_head_request_detail", pk=pk)

        # === Assign Personnel & Materials ===
        if action == "assign" and service_request.status not in ["Done for Review", "Completed"]:
            service_request.assigned_personnel.set(request.POST.getlist("personnel_ids"))

            # Reset and return materials to inventory
            for rm in service_request.requestmaterial_set.all():
                rm.material.quantity += rm.quantity
                rm.material.save()
            service_request.requestmaterial_set.all().delete()

            material_ids = request.POST.getlist("material_ids")
            for material_id in material_ids:
                qty = request.POST.get(f"quantity_{material_id}")
                if qty and int(qty) > 0:
                    material = get_object_or_404(
                        InventoryItem, pk=material_id, owned_by=service_request.unit
                    )
                    qty = int(qty)
                    if material.quantity < qty:
                        messages.error(request, f"Not enough {material.name}.")
                        return redirect("gso_requests:unit_head_request_detail", pk=pk)

                    material.quantity -= qty
                    material.save()

                    RequestMaterial.objects.create(
                        request=service_request,
                        material=material,
                        quantity=qty
                    )

            messages.success(request, "✅ Assignments updated successfully.")
            return redirect("gso_requests:unit_head_request_detail", pk=pk)

        # === Approve Completion (Generate WAR) ===
        elif action == "approve" and service_request.status == "Done for Review":
            service_request.status = "Completed"
            service_request.completed_at = timezone.now()
            service_request.save(update_fields=["status", "completed_at"])

            war = create_war_from_request(service_request)

            if war and service_request.selected_indicator:
                war.success_indicator = service_request.selected_indicator
                war.save(update_fields=["success_indicator"])

            messages.success(request, "✅ Request marked as Completed. WAR created.")
            return redirect("gso_requests:unit_head_request_detail", pk=pk)

        # === Reject Completion ===
        elif action == "reject" and service_request.status == "Done for Review":
            service_request.status = "In Progress"
            service_request.save(update_fields=["status"])
            messages.warning(request, "⚠️ Request sent back to In Progress.")
            return redirect("gso_requests:unit_head_request_detail", pk=pk)

    # --- Assigned Materials (for editing) ---
    assigned_materials = {
        rm.material.id: rm.quantity for rm in service_request.requestmaterial_set.all()
    }

    # --- Render Template ---
    return render(request, "unit_heads/unit_head_request_management/request_detail.html", {
        "req": service_request,
        "personnel": available_personnel,       # 👈 only show available personnel
        "busy_personnel": busy_personnel,       # 👈 optional if you want to show busy list
        "materials": materials,
        "reports": reports,
        "assigned_materials": assigned_materials,
        "war": war,
        "indicators": indicators,
    })


@login_required
@user_passes_test(is_unit_head)
def unit_head_request_history(request):
    requests_qs = ServiceRequest.objects.filter(
        unit=request.user.unit,
        status__in=["Completed", "Cancelled"]
    ).order_by("-created_at")

    requests_qs = filter_requests(requests_qs, search_query=request.GET.get("q"))
    return render(request, "unit_heads/unit_head_request_history/unit_head_request_history.html", {
        "requests": requests_qs
    })



@login_required
def unit_head_material_detail(request, item_id):
    item = get_object_or_404(InventoryItem, id=item_id)
    return render(request, "unit_heads/unit_head_inventory/unit_head_material_detail.html", {
        "material": item,
    })







# -------------------------------
# Personnel Views
# -------------------------------
@login_required
def personnel_task_management(request):
    tasks = ServiceRequest.objects.filter(assigned_personnel=request.user).exclude(status__in=["Completed", "Cancelled"]).distinct()
    tasks = filter_requests(tasks, search_query=request.GET.get("q"), status_filter=request.GET.get("status"))
    return render(request, "personnel/personnel_task_management/personnel_task_management.html", {"tasks": tasks})


@login_required
def personnel_task_detail(request, pk):
    from apps.gso_reports.models import SuccessIndicator  # avoid circular import

    task = get_object_or_404(ServiceRequest, pk=pk, assigned_personnel=request.user)
    materials = task.requestmaterial_set.select_related("material")
    reports = task.reports.select_related("personnel").order_by("-created_at")
    indicators = SuccessIndicator.objects.filter(is_active=True).order_by("code")  # list of all indicators

    if request.method == "POST":
        # Start Task
        if "start" in request.POST and task.status == "Approved":
            task.status = "In Progress"
            task.started_at = timezone.now()
            task.save()

        # Mark Done
        elif "done" in request.POST and task.status == "In Progress":
            # Save selected indicator before marking done
            indicator_id = request.POST.get("success_indicator")
            if indicator_id:
                try:
                    task.selected_indicator_id = int(indicator_id)
                    task.save(update_fields=["selected_indicator"])
                except ValueError:
                    pass

            task.status = "Done for Review"
            task.done_at = timezone.now()
            task.save()

        # Add Report
        elif "add_report" in request.POST:
            report_text = request.POST.get("report_text", "").strip()
            if report_text:
                TaskReport.objects.create(request=task, personnel=request.user, report_text=report_text)

        # Save Indicator Only (without changing status)
        elif "save_indicator" in request.POST:
            indicator_id = request.POST.get("success_indicator")
            if indicator_id:
                try:
                    task.selected_indicator_id = int(indicator_id)
                    task.save(update_fields=["selected_indicator"])
                    messages.success(request, "Success indicator saved.")
                except ValueError:
                    messages.error(request, "Invalid indicator selected.")

        return redirect("gso_requests:personnel_task_detail", pk=task.id)

    return render(request, "personnel/personnel_task_management/personnel_task_detail.html", {
        "task": task,
        "materials": materials,
        "reports": reports,
        "indicators": indicators,
    })

@login_required
def personnel_history(request):
    history = ServiceRequest.objects.filter(assigned_personnel=request.user, status="Completed").order_by("-created_at")
    return render(request, "personnel/personnel_history/personnel_history.html", {"history": history})


@login_required
def personnel_inventory(request):
    materials = get_unit_inventory(request.user.unit, search_query=request.GET.get("q"))
    return render(request, "personnel/personnel_inventory/personnel_inventory.html", {"materials": materials})


# -------------------------------
# Requestor Views
# -------------------------------
@login_required
@user_passes_test(is_requestor)
def requestor_request_management(request):
    requests_qs = ServiceRequest.objects.filter(requestor=request.user).order_by("-created_at")
    units = Unit.objects.all()
    return render(request, "requestor/requestor_request_management/requestor_request_management.html", {
        "requests": requests_qs,
        "units": units,
    })


@login_required
@user_passes_test(is_requestor)
def add_request(request):
    if request.method == "POST":
        ServiceRequest.objects.create(
            requestor=request.user,
            unit_id=request.POST.get("unit"),
            description=request.POST.get("description"),
            status="Pending",
            department=request.user.department,
            custom_full_name=request.POST.get("custom_full_name") or "",
            custom_email=request.POST.get("custom_email") or "",
            custom_contact_number=request.POST.get("custom_contact_number") or "",
            attachment=request.FILES.get("attachment"),  # 👈 Handle file upload
        )
        return redirect("gso_requests:requestor_request_management")


@login_required
@user_passes_test(is_requestor)
def cancel_request(request, pk):
    req = get_object_or_404(ServiceRequest, pk=pk, requestor=request.user)
    if req.status in ["Pending", "Approved"]:
        req.status = "Cancelled"
        req.save()
    return redirect("gso_requests:requestor_request_management")


@login_required
@user_passes_test(is_requestor)
def requestor_request_history(request):
    history = ServiceRequest.objects.filter(
        requestor=request.user,
        status__in=["Completed", "Cancelled"]
    ).order_by("-created_at")
    return render(request, "requestor/requestor_request_history/requestor_request_history.html", {
        "request_history": history
    })




# -------------------------------
# SUCCESS INDICATOR (Personnel + Unit Head)
# -------------------------------

@login_required
def update_success_indicator_personnel(request, request_id):
    """
    Allow assigned personnel to propose/update a success indicator for their completed task.
    """
    service_request = get_object_or_404(ServiceRequest, id=request_id, assigned_personnel=request.user)
    war = WorkAccomplishmentReport.objects.filter(request=service_request).first()

    if not war:
        messages.error(request, "No Work Accomplishment Report found for this request.")
        return redirect("gso_requests:personnel_task_detail", pk=request_id)

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            indicator, _ = SuccessIndicator.objects.get_or_create(name=name)
            if description:
                indicator.description = description
                indicator.save(update_fields=["description"])
            war.success_indicator = indicator
            war.save(update_fields=["success_indicator"])
            messages.success(request, "Success Indicator updated successfully.")
            return redirect("gso_requests:personnel_task_detail", pk=request_id)

        messages.warning(request, "Indicator name is required.")

    return render(request, "personnel/personnel_success_indicator_form.html", {
        "task": service_request,
        "war": war,
    })


@login_required
def update_success_indicator_unit_head(request, request_id):
    """
    Allow Unit Head to review/update a success indicator for their unit’s request.
    """
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    war = WorkAccomplishmentReport.objects.filter(request=service_request).first()

    if not war:
        messages.error(request, "No Work Accomplishment Report found for this request.")
        return redirect("gso_requests:unit_head_request_detail", pk=request_id)

    # Restrict to same unit
    if request.user.role != "unit_head" or service_request.unit != request.user.unit:
        return HttpResponseForbidden("Not authorized to edit this indicator.")

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        description = request.POST.get("description", "").strip()

        if name:
            indicator, _ = SuccessIndicator.objects.get_or_create(name=name)
            if description:
                indicator.description = description
                indicator.save(update_fields=["description"])
            war.success_indicator = indicator
            war.save(update_fields=["success_indicator"])
            messages.success(request, "Success Indicator updated successfully.")
            return redirect("gso_requests:unit_head_request_detail", pk=request_id)

        messages.warning(request, "Indicator name is required.")

    return render(request, "unit_head/unit_head_success_indicator_form.html", {
        "req": service_request,
        "war": war,
    })
