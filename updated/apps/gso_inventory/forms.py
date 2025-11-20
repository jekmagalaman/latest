from django import forms
from .models import InventoryItem

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ["name", "category", "quantity", "unit_of_measurement", "description", "owned_by"]
        labels = {
            "name": "Material Name",
            "category": "Category",
            "quantity": "Quantity",
            "unit_of_measurement": "Unit",
            "description": "Description",
            "owned_by": "Unit Owner",
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # 👇 AUTOMATICALLY REMOVE "owned_by" WHEN UNIT HEAD IS ADDING
        if user and getattr(user, "role", None) == "unit_head":
            self.fields.pop("owned_by", None)
