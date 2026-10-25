from django import forms
from .models import Order
import re


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["full_name", "phone", "wilaya", "address", "notes"]
        widgets = {"notes": forms.Textarea(attrs={"rows": 2})}

    def clean_phone(self):
        phone = re.sub(r"[\s.\-]", "", self.cleaned_data["phone"])
        if not re.fullmatch(r"\+?\d{8,15}", phone):
            raise forms.ValidationError("Enter a valid phone number, e.g. 0555 12 34 56.")
        return phone
