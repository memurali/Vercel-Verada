# apps/users/forms.py
from django import forms
import re

class OTPForm(forms.Form):
    session_token = forms.UUIDField(widget=forms.HiddenInput())

    otp = forms.CharField(
        label="OTP",
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter 6-digit OTP"}),
    )

    def clean_otp(self):
        otp = self.cleaned_data['otp']
        if not re.fullmatch(r"\d{6}", otp):
            raise forms.ValidationError("OTP must be exactly 6 digits (numbers only).")
        return otp
