from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.gso_accounts.models import Unit, Department
from apps.gso_inventory.models import InventoryItem
from apps.gso_reports.models import SuccessIndicator 
from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField


class ServiceRequest(models.Model):
    auditlog_history = AuditlogHistoryField()
    """
    Represents a service request submitted by a user (requestor).
    Tracks workflow status, assigned personnel, and requested materials.
    """

    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Approved", "Approved"),
        ("In Progress", "In Progress"),
        ("Done for Review", "Done for Review"),
        ("Completed", "Completed"),
        ("Cancelled", "Cancelled"),
        ("Emergency", "Emergency"),
    ]

    # Who made the request
    requestor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="requests"
    )
    unit = models.ForeignKey(Unit, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)

    # If request is made on behalf of someone else
    custom_full_name = models.CharField(max_length=255, blank=True, null=True)
    custom_email = models.EmailField(blank=True, null=True)
    custom_contact_number = models.CharField(max_length=50, blank=True, null=True)
    attachment_link = models.URLField(max_length=500, blank=True, null=True)


    # Request categories chosen by the requestor
    labor = models.BooleanField(default=False)
    materials_needed = models.BooleanField(default=False)
    others_needed = models.BooleanField(default=False)

    
    # 🚨 Emergency flag
    is_emergency = models.BooleanField(default=False)

    # Scheduling
    schedule_start = models.DateTimeField(null=True, blank=True)
    schedule_end = models.DateTimeField(null=True, blank=True)
    schedule_remarks = models.TextField(null=True, blank=True)

    # Details
    activity_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Short standardized activity name (auto-mapped from description)"
    )
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    cancel_reason = models.TextField(null=True, blank=True)

    # Assignment
    assigned_personnel = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="assigned_requests"
    )

    # Materials used
    materials = models.ManyToManyField(
        InventoryItem,
        through="RequestMaterial",
        blank=True,
        related_name="requests"
    )

    # ✅ Personnel-chosen success indicator
    selected_indicator = models.ForeignKey(
        SuccessIndicator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="selected_for_requests",
        help_text="Temporary field where personnel can choose success indicator before WAR generation."
    )

    # === GLOBAL DEFAULT ORDERING (Emergency requests first) ===
    class Meta:
        ordering = ['-is_emergency', '-created_at']

    def __str__(self):
        display_name = self.custom_full_name or self.requestor.get_full_name()
        return f"Request #{self.id} by {display_name} - {self.unit.name}"

    @property
    def assigned_personnel_names(self):
        personnel = self.assigned_personnel.all()
        if personnel.exists():
            return ", ".join([p.get_full_name() or p.username for p in personnel])
        return ""
    

# ----------------------------------------- #
#   Motorpool ServiceRequest Related Models #
# ----------------------------------------- #

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=50, unique=True)
    make_model = models.CharField(max_length=200, blank=True, null=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)  # passengers
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.plate_number} — {self.make_model or 'Unknown'}"

class MotorpoolRequest(models.Model):
    """
    Motorpool-specific details that attach to a ServiceRequest.
    """
    service_request = models.OneToOneField(
        'ServiceRequest', on_delete=models.CASCADE, related_name='motorpool'
    )

    # vehicle only
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)

    # request details
    requesting_office = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )

    purpose = models.TextField(blank=True, null=True)
    place_to_be_visited = models.CharField(max_length=255, blank=True, null=True)
    trip_start = models.DateTimeField(null=True, blank=True)
    trip_end = models.DateTimeField(null=True, blank=True)
    itinerary = models.TextField(blank=True, null=True)
    passengers_count = models.PositiveIntegerField(null=True, blank=True)
    contact_no = models.CharField(max_length=50, blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    number_of_days = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Motorpool details for Request #{self.service_request.id}"


# Fuel PO and line items for Purchase Order for Fuel & Lubricants
class FuelProduct(models.TextChoices):
    DIESEL = "Diesel", "Diesel"
    GAS_UNLEADED = "Gasoline - Unleaded", "Gasoline - Unleaded"
    GAS_REGULAR = "Gasoline - Regular", "Gasoline - Regular"

class FuelPurchaseOrder(models.Model):
    service_request = models.OneToOneField('ServiceRequest', on_delete=models.CASCADE, related_name='fuel_po')
    requesting_office = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True
    )
    purpose = models.TextField(blank=True, null=True)
    driver_or_official = models.CharField(max_length=255, blank=True, null=True)
    vehicle_plate = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fuel PO for Request #{self.service_request.id}"

class FuelPurchaseLineItem(models.Model):
    po = models.ForeignKey(FuelPurchaseOrder, on_delete=models.CASCADE, related_name='lines')
    product = models.CharField(max_length=50, choices=FuelProduct.choices)
    qty_words = models.CharField(max_length=255, blank=True, null=True)
    qty_figure = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.product} — {self.qty_figure or 0}"



class RequestMaterial(models.Model):
    auditlog_history = AuditlogHistoryField()
    """Through model for materials used in a request."""
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE)
    material = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.material.name} x {self.quantity} (Request #{self.request.id})"


class TaskReport(models.Model):
    auditlog_history = AuditlogHistoryField()
    """Individual report written by personnel assigned to a request."""
    request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name="reports")
    personnel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    report_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TaskReport by {self.personnel} (Request #{self.request.id})"
    


class Feedback(models.Model):
    auditlog_history = AuditlogHistoryField()
    """Feedback form tied to a specific service request."""
    request = models.OneToOneField(ServiceRequest, on_delete=models.CASCADE, related_name='feedback')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Citizen’s Charter Questions (Part I)
    cc1 = models.CharField(max_length=200, blank=True, verbose_name="Awareness of Citizen's Charter")
    cc2 = models.CharField(max_length=200, blank=True, verbose_name="Knowledge of Office CC")
    cc3 = models.CharField(max_length=200, blank=True, verbose_name="Usefulness of CC")

    # Service Quality Dimensions (Part II)
    sqd1 = models.IntegerField(null=True, blank=True, verbose_name="Staff were courteous and helpful")
    sqd2 = models.IntegerField(null=True, blank=True, verbose_name="Spent reasonable time for transaction")
    sqd3 = models.IntegerField(null=True, blank=True, verbose_name="Clear communication during process")
    sqd4 = models.IntegerField(null=True, blank=True, verbose_name="Accessible and adequate facilities")
    sqd5 = models.IntegerField(null=True, blank=True, verbose_name="Equipped and knowledgeable staff")
    sqd6 = models.IntegerField(null=True, blank=True, verbose_name="Transparent and fair service")
    sqd7 = models.IntegerField(null=True, blank=True, verbose_name="Services met expectations")
    sqd8 = models.IntegerField(null=True, blank=True, verbose_name="Satisfied with overall experience")
    sqd9 = models.IntegerField(null=True, blank=True, verbose_name="Would recommend the service")

    # Optional Suggestions & Contact
    suggestions = models.TextField(blank=True, verbose_name="Suggestions for improvement")
    email = models.EmailField(blank=True, null=True, verbose_name="Email address (optional)")

    # Analytics Fields
    average_score = models.FloatField(default=0, verbose_name="Average satisfaction score")
    sentiment = models.CharField(max_length=20, blank=True, verbose_name="Sentiment (AI-generated)")
    is_visible = models.BooleanField(default=True, verbose_name="Visible in reports")

    date_submitted = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Automatically compute average score when saving."""
        scores = [
            self.sqd1, self.sqd2, self.sqd3, self.sqd4,
            self.sqd5, self.sqd6, self.sqd7, self.sqd8, self.sqd9
        ]
        valid_scores = [s for s in scores if s is not None]
        self.average_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Feedback for Request #{self.request.id} by {self.user.username}"







# -----------------------------
# Register ServiceRequest with Auditlog
# -----------------------------
auditlog.register(
    ServiceRequest,
    m2m_fields={"assigned_personnel", "materials"},  # Track changes on M2M
    serialize_data=True,                              # Store entire state
    serialize_auditlog_fields_only=True               # Only include fields tracked by Auditlog
)
#auditlog.register(ServiceRequest) #new
auditlog.register(TaskReport) #new
auditlog.register(RequestMaterial) #new
    
