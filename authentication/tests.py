from unittest.mock import MagicMock, patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from authentication.views.google_auth_view import _build_registration_token
from otp.tokens import issue_verification_token
from user.models import User

TEST_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


@override_settings(CACHES=TEST_CACHES)
class GoogleCompleteViewTests(APITestCase):

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def _registration_token(self, sub="google-sub-1"):
        return _build_registration_token(sub, "person@example.com", "Person", "")

    def test_missing_verification_token_rejected(self):
        response = self.client.post(
            "/auth/google/complete/",
            {
                "token": self._registration_token(),
                "username": "newuser",
                "phone": "+919876543210",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)

    def test_verification_token_for_wrong_phone_rejected(self):
        verification_token = issue_verification_token("+919876543299", "user_signup")

        response = self.client.post(
            "/auth/google/complete/",
            {
                "token": self._registration_token(),
                "username": "newuser",
                "phone": "+919876543210",
                "verification_token": verification_token,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(User.objects.count(), 0)

    def test_valid_verification_token_creates_verified_user(self):
        verification_token = issue_verification_token("+919876543210", "user_signup")

        response = self.client.post(
            "/auth/google/complete/",
            {
                "token": self._registration_token(),
                "username": "newuser",
                "phone": "+919876543210",
                "verification_token": verification_token,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="newuser")
        self.assertTrue(user.phone_verified)
        self.assertIsNotNone(user.phone_verified_at)
