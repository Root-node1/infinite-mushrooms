import re

from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


def normalize_phone(raw):
    """Store every number as E.164, defaulting local 07xx numbers to Kenya."""
    phone = re.sub(r"[\s\-()]", "", raw or "")
    if phone.startswith("00"):
        phone = "+" + phone[2:]
    elif phone.startswith("0") and len(phone) == 10:
        phone = "+254" + phone[1:]
    elif phone.startswith("254"):
        phone = "+" + phone
    if not re.fullmatch(r"\+\d{10,15}", phone):
        raise ValueError("Enter a valid phone number, e.g. +254712345678")
    return phone


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("A phone number is required")
        user = self.model(phone=normalize_phone(phone), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        OWNER = "owner", "Farm owner"
        STAFF = "staff", "Farm staff"

    phone = models.CharField(max_length=16, unique=True)
    full_name = models.CharField(max_length=150)
    email = models.EmailField(blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.OWNER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["full_name"]

    def save(self, *args, **kwargs):
        self.phone = normalize_phone(self.phone)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"
