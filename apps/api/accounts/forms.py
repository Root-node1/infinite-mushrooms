from django import forms
from django.contrib.auth.forms import BaseUserCreationForm, UserChangeForm

from .models import User, normalize_phone


class PhoneCleanMixin:
    def clean_phone(self):
        try:
            return normalize_phone(self.cleaned_data["phone"])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class UserCreationForm(PhoneCleanMixin, BaseUserCreationForm):
    class Meta:
        model = User
        fields = ("phone", "full_name", "role")


class UserAdminChangeForm(PhoneCleanMixin, UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"
