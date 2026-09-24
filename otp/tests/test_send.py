from django.core.cache import cache
from rest_framework import status

from hotel.models import Hotel
from user.models import User

from .base import OtpAPITestCase

SEND_URL = "/otp/send/"


def make_hotel(phone_number="+919876543210"):
    return Hotel.objects.create(name="Test Hotel", address="123 St", city="Testville", phone_number=phone_number)


def make_user(phone="+919876543211", username="tester"):
    return User.objects.create_user(username=username, phone=phone)


class SendOtpTests(OtpAPITestCase):

    def test_invalid_phone_returns_400(self):
        response = self.client.post(SEND_URL, {"phone": "123", "purpose": "hotel_signup"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.mock_verifications.create.assert_not_called()

    def test_invalid_purpose_returns_400(self):
        response = self.client.post(SEND_URL, {"phone": "+919876543210", "purpose": "nonsense"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_hotel_signup_new_phone_sends_otp(self):
        response = self.client.post(
            SEND_URL, {"phone": "+919876543210", "purpose": "hotel_signup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_verifications.create.assert_called_once()

    def test_hotel_signup_existing_phone_rejected(self):
        make_hotel(phone_number="+919876543210")
        response = self.client.post(
            SEND_URL, {"phone": "+919876543210", "purpose": "hotel_signup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.mock_verifications.create.assert_not_called()

    def test_user_signup_existing_phone_rejected(self):
        make_user(phone="+919876543211")
        response = self.client.post(
            SEND_URL, {"phone": "+919876543211", "purpose": "user_signup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.mock_verifications.create.assert_not_called()

    def test_hotel_login_unregistered_phone_returns_generic_success(self):
        response = self.client.post(
            SEND_URL, {"phone": "+919876543212", "purpose": "hotel_login"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_verifications.create.assert_not_called()

    def test_hotel_login_registered_phone_sends_otp(self):
        make_hotel(phone_number="+919876543212")
        response = self.client.post(
            SEND_URL, {"phone": "+919876543212", "purpose": "hotel_login"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.mock_verifications.create.assert_called_once()

    def test_password_reset_unregistered_and_registered_give_same_response(self):
        unregistered = self.client.post(
            SEND_URL, {"phone": "+919876543213", "purpose": "password_reset"}, format="json"
        )
        make_hotel(phone_number="+919876543214")
        registered = self.client.post(
            SEND_URL, {"phone": "+919876543214", "purpose": "password_reset"}, format="json"
        )
        self.assertEqual(unregistered.status_code, status.HTTP_200_OK)
        self.assertEqual(registered.status_code, status.HTTP_200_OK)
        self.assertEqual(unregistered.data["message"], registered.data["message"])
        self.mock_verifications.create.assert_called_once()

    def test_resend_within_cooldown_returns_429(self):
        first = self.client.post(
            SEND_URL, {"phone": "+919876543215", "purpose": "hotel_signup"}, format="json"
        )
        self.assertEqual(first.status_code, status.HTTP_200_OK)

        second = self.client.post(
            SEND_URL, {"phone": "+919876543215", "purpose": "hotel_signup"}, format="json"
        )
        self.assertEqual(second.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn("seconds_remaining", second.data["data"])

    def test_resend_after_cooldown_clears_succeeds(self):
        self.client.post(SEND_URL, {"phone": "+919876543216", "purpose": "hotel_signup"}, format="json")
        cache.delete("otp:cooldown:hotel_signup:+919876543216")

        response = self.client.post(
            SEND_URL, {"phone": "+919876543216", "purpose": "hotel_signup"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.mock_verifications.create.call_count, 2)
