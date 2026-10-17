from django.contrib.auth import authenticate, get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

User = get_user_model()


class UserTests(TestCase):
    def test_local_number_is_normalised(self):
        user = User.objects.create_user("0712 345 678", password="pw", full_name="Amina")
        self.assertEqual(user.phone, "+254712345678")

    def test_invalid_phone_is_rejected(self):
        with self.assertRaises(ValueError):
            User.objects.create_user("123", password="pw", full_name="Bad")

    def test_duplicate_phone_is_rejected(self):
        User.objects.create_user("0712345678", password="pw", full_name="A")
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user("+254712345678", password="pw", full_name="B")

    def test_login_with_phone(self):
        User.objects.create_user("0712345678", password="pw", full_name="A")
        self.assertIsNotNone(authenticate(phone="+254712345678", password="pw"))

    def test_superuser_flags(self):
        admin = User.objects.create_superuser("0700000000", password="pw", full_name="Admin")
        self.assertTrue(admin.is_staff and admin.is_superuser)


class PhoneBackendTests(TestCase):
    def setUp(self):
        User.objects.create_user("0712345678", password="pw", full_name="A")

    def test_login_with_local_format(self):
        self.assertIsNotNone(authenticate(username="0712345678", password="pw"))

    def test_login_with_international_format(self):
        self.assertIsNotNone(authenticate(username="+254712345678", password="pw"))

    def test_wrong_password_and_garbage_phone_fail(self):
        self.assertIsNone(authenticate(username="0712345678", password="nope"))
        self.assertIsNone(authenticate(username="abc", password="pw"))

    def test_admin_login_with_local_format(self):
        self.assertTrue(self.client.login(username="0712345678", password="pw"))
