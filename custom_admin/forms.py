# custom_admin/forms.py
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from Handyman.models import Category, ServiceProvider


class AdminUserCreationForm(UserCreationForm):
    is_staff = forms.BooleanField(required=False, label="Can access Django admin")
    is_superuser = forms.BooleanField(required=False, label="Superuser (all permissions)")

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ("username", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data["is_staff"]
        user.is_superuser = self.cleaned_data["is_superuser"]
        if commit:
            user.save()
        return user


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", "is_active", "is_staff", "is_superuser")


class AdminCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'slug']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class AdminProviderForm(forms.ModelForm):
    class Meta:
        model = ServiceProvider
        # FIXED: Removed 'business_name' and 'is_approved'. Used your exact models.py fields:
        fields = ['name', 'category', 'description', 'address', 'city', 'state', 'phone', 'status']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'category': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg', 'rows': 3}),
            'address': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'city': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'state': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
            'status': forms.Select(attrs={'class': 'w-full p-2 border border-gray-300 rounded-lg'}),
        }
