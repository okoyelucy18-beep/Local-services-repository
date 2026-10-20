
from django import forms
from .models import ServiceProvider


class ServiceProviderRegistrationForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        fields = [
            "name",
            "category",
            "description",
            "address",
            "state",
            "city",
            "neighborhood",
            "phone",
            "email",
            "website",
            "image",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "name": forms.TextInput(
                attrs={"placeholder": "Business name"}
            ),
            "address": forms.TextInput(
                attrs={"placeholder": "Street address"}
            ),
            "state": forms.TextInput(
                attrs={"placeholder": "State, e.g. Anambra"}
            ),
            "city": forms.TextInput(
                attrs={"placeholder": "City, e.g. Onitsha"}
            ),
            "neighborhood": forms.TextInput(
                attrs={"placeholder": "Neighborhood, e.g. Fegge"}
            ),
            "phone": forms.TextInput(
                attrs={"placeholder": "Business phone number"}
            ),
        }

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if len(name) < 2:
            raise forms.ValidationError(
                "Business name must contain at least 2 characters."
            )
        return name

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()
        if len(phone) < 7:
            raise forms.ValidationError(
                "Enter a valid business phone number."
            )
        return phone
