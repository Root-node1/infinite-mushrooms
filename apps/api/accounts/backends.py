from django.contrib.auth.backends import ModelBackend

from .models import normalize_phone


class PhoneBackend(ModelBackend):
    """Accept 0712..., 254712... or +254712... at login."""

    def authenticate(self, request, username=None, password=None, **kwargs):
        phone = username if username is not None else kwargs.get("phone")
        if phone is None or password is None:
            return None
        try:
            phone = normalize_phone(phone)
        except ValueError:
            return None
        return super().authenticate(request, username=phone, password=password)
