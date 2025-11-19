from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()


class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter password"}),
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm password"}),
        label="Confirm Password"
    )

    class Meta:
        model = User
        fields = [
            "role",
            "unit",
            "position",
            "employment_status",
            "username",
            "first_name",
            "last_name",
            "email",
            "department",
            "account_status",
            "password",
            "confirm_password",
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        unit = cleaned_data.get("unit")
        position = cleaned_data.get("position")
        employment_status = cleaned_data.get("employment_status")
        department = cleaned_data.get("department")
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # 🔐 Password match
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        # ==============================
        # ROLE-BASED FORM VALIDATION
        # ==============================

        # ❌ DIRECTOR & REQUESTOR cannot have position or employment status
        if role in ["director", "requestor"]:
            if position:
                raise forms.ValidationError(f"{role.title()} must NOT have a position.")
            if employment_status:
                raise forms.ValidationError(f"{role.title()} must NOT have an employment status.")

        # REQUESTOR → must have department, no unit
        if role == "requestor":
            if not department:
                raise forms.ValidationError("Requestor must have a department assigned.")
            if unit:
                raise forms.ValidationError("Requestor cannot belong to a unit.")

        # DIRECTOR & GSO → no unit, no department
        if role in ["director", "gso"]:
            if unit:
                raise forms.ValidationError(f"{role.title()} must NOT belong to a unit.")
            if department:
                raise forms.ValidationError(f"{role.title()} must NOT belong to a department.")

        # UNIT HEAD & PERSONNEL → must have unit + position + employment status
        if role in ["unit_head", "personnel"]:
            if not unit:
                raise forms.ValidationError(f"{role.title()} must belong to a unit.")
            if not position:
                raise forms.ValidationError(f"{role.title()} must have a position.")
            if not employment_status:
                raise forms.ValidationError(f"{role.title()} must have an employment status.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user



class UserEditForm(forms.ModelForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'autocomplete': 'off'}),
        required=False,
        label="Old Password",
        help_text="Optional: Fill only if you want to change the password."
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Enter new password"}),
        required=False,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm new password"}),
        required=False,
        label="Confirm New Password"
    )

    class Meta:
        model = User
        fields = [
            "username",
            "role",
            "unit",
            "position",
            "employment_status",
            "first_name",
            "last_name",
            "email",
            "department",
            "account_status",
        ]

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        unit = cleaned_data.get("unit")
        position = cleaned_data.get("position")
        employment_status = cleaned_data.get("employment_status")
        department = cleaned_data.get("department")

        old_pass = cleaned_data.get("old_password")
        new_pass = cleaned_data.get("new_password")
        confirm_pass = cleaned_data.get("confirm_password")

        # ====================
        # PASSWORD UPDATE RULES
        # ====================
        if new_pass or confirm_pass:
            if new_pass != confirm_pass:
                raise forms.ValidationError("New password and confirmation do not match.")

            if not old_pass:
                raise forms.ValidationError("Enter old password to set a new password.")

            if not self.instance.check_password(old_pass):
                raise forms.ValidationError("Old password is incorrect.")

        # ====================
        # ROLE-BASED VALIDATION
        # ====================

        if role in ["director", "requestor"]:
            if position:
                raise forms.ValidationError(f"{role.title()} must NOT have a position.")
            if employment_status:
                raise forms.ValidationError(f"{role.title()} must NOT have an employment status.")

        if role == "requestor":
            if not department:
                raise forms.ValidationError("Requestor must have a department.")
            if unit:
                raise forms.ValidationError("Requestor cannot belong to a unit.")

        if role in ["director", "gso"]:
            if unit:
                raise forms.ValidationError(f"{role.title()} must not belong to a unit.")
            if department:
                raise forms.ValidationError(f"{role.title()} must not belong to a department.")

        if role in ["unit_head", "personnel"]:
            if not unit:
                raise forms.ValidationError(f"{role.title()} must belong to a unit.")
            if not position:
                raise forms.ValidationError(f"{role.title()} must have a position.")
            if not employment_status:
                raise forms.ValidationError(f"{role.title()} must have an employment status.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        new_pass = self.cleaned_data.get("new_password")
        if new_pass:
            user.set_password(new_pass)
        if commit:
            user.save()
        return user



class RequestorProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["department", "email"]