from django.contrib import admin
from .models import ServiceRequest, RequestMaterial, TaskReport

from auditlog.mixins import AuditlogHistoryAdminMixin
from auditlog.models import LogEntry


admin.site.register(RequestMaterial)
admin.site.register(TaskReport)


@admin.register(ServiceRequest)
class ServiceRequestAdmin(AuditlogHistoryAdminMixin, admin.ModelAdmin):
    """
    Admin for ServiceRequest that shows:
      - who made the latest change (last_modified_by)
      - JSON audit details of the latest change (latest_change_json)
      - "View History" button via AuditlogHistoryAdminMixin
    """

    list_display = ("id", "status", "created_at", "last_modified_by")
    search_fields = ("id", "description", "requestor__username")
    list_filter = ("status", "created_at")

    # Show these inside the service request edit page
    readonly_fields = ("last_modified_by", "latest_change_json")

    show_auditlog_history_link = True
    auditlog_history_per_page = 20

    # ---------------------------
    # Helper: get latest LogEntry
    # ---------------------------
    def get_latest_log_entry(self, obj):
        if obj is None:
            return None
        return LogEntry.objects.get_for_object(obj).order_by("-timestamp").first()

    # -----------------------------------------
    # Show the actor (user) who last modified it
    # -----------------------------------------
    def last_modified_by(self, obj):
        last = self.get_latest_log_entry(obj)
        if not last:
            return "—"

        actor = last.actor  # user instance OR None

        if actor:
            return str(actor)

        # Fallback to identity string or IP
        if last.actor_display:
            return last.actor_display

        if last.remote_addr:
            return f"IP: {last.remote_addr}"

        return "—"

    last_modified_by.short_description = "Last modified by"

    # ---------------------------------------------------------
    # Display raw JSON of the latest change inside the form page
    # ---------------------------------------------------------
    def latest_change_json(self, obj):
    #"""
    #Display the latest audit log change as pretty JSON,
    #resolving all M2M fields (added/removed) to readable names if possible.
    #"""
        last = self.get_latest_log_entry(obj)
        if not last:
            return "No audit log entries."

        import json
        from django.utils.html import format_html
        from apps.gso_accounts.models import User  # for assigned_personnel

        data = last.changes or {}

        # Iterate through all M2M fields in the changes
        for field_name, m2m in data.items():
            if isinstance(m2m, dict) and "added" in m2m and "removed" in m2m:
                resolved_added = []
                resolved_removed = []

                # Determine model dynamically if possible
                field = getattr(obj.__class__, field_name, None)
                model = getattr(getattr(field, "rel", None), "model", None)  # for older Django
                if not model:
                    try:
                        # Fallback: assume assigned_personnel = User
                        if field_name == "assigned_personnel":
                            model = User
                    except:
                        model = None

                # Resolve 'added'
                for pk in m2m["added"]:
                    if model:
                        try:
                            resolved_added.append(str(model.objects.get(pk=pk)))
                        except model.DoesNotExist:
                            resolved_added.append(f"{model.__name__}({pk})")
                    else:
                        resolved_added.append(str(pk))
                m2m["added"] = resolved_added

                # Resolve 'removed'
                for pk in m2m["removed"]:
                    if model:
                        try:
                            resolved_removed.append(str(model.objects.get(pk=pk)))
                        except model.DoesNotExist:
                            resolved_removed.append(f"{model.__name__}({pk})")
                    else:
                        resolved_removed.append(str(pk))
                m2m["removed"] = resolved_removed

                data[field_name] = m2m

        pretty = json.dumps(data, indent=2, default=str)
        return format_html("<pre style='max-height:300px; overflow:auto;'>{}</pre>", pretty)
