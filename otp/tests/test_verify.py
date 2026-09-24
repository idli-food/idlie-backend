from unittest.mock import MagicMock

from rest_framework import status
from twilio.base.exceptions import TwilioRestException

from authentication.jwt.jwt_utils import decode_token
from hotel.models import Hotel

from .base import OtpAPITestCase

SEND_URL = "/otp/send/"
VERIFY_URL = "/otp/verify/"


def make_hotel(phone_number="+919876543210"):
    return Hotel.objects.create(name="Test Hotel", address="123 St", city="Testville", phone_number=phone_number)


class VerifyOtpTests(OtpAPITestCase):

    def _send(self, phone, purpose):
        return self.client.post(SEND_URL, {"phone": phone, "purpose": purpose}, format="json")

    def test_verify_without_pending_entry_returns_410(self):
        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_approved_code_returns_verification_token(self):
        self._send("+919876543210", "hotel_signup")
        self.mock_verification_checks.create.return_value = MagicMock(status="approved")

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("verification_token", response.data["data"])

    def test_wrong_code_returns_401(self):
        self._send("+919876543210", "hotel_signup")
        self.mock_verification_checks.create.return_value = MagicMock(status="pending")

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "000000"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_twilio_404_maps_to_410(self):
        self._send("+919876543210", "hotel_signup")
        self.mock_verification_checks.create.side_effect = TwilioRestException(404, "uri", "not found")

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_410_GONE)

    def test_twilio_max_attempts_maps_to_429(self):
        self._send("+919876543210", "hotel_signup")
        self.mock_verification_checks.create.side_effect = TwilioRestException(
            400, "uri", "max attempts", code=60202
        )

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_twilio_invalid_number_maps_to_400(self):
        self._send("+919876543210", "hotel_signup")
        self.mock_verification_checks.create.side_effect = TwilioRestException(
            400, "uri", "invalid", code=60200
        )

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_twilio_fraud_block_maps_to_403(self):
        self._send("+919876543210", "hotel_signup")
        self.mock_verification_checks.create.side_effect = TwilioRestException(
            400, "uri", "fraud", code=60410
        )

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_signup", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_hotel_login_success_issues_tokens(self):
        hotel = make_hotel(phone_number="+919876543210")
        self._send("+919876543210", "hotel_login")
        self.mock_verification_checks.create.return_value = MagicMock(status="approved")

        response = self.client.post(
            VERIFY_URL,
            {"phone": "+919876543210", "purpose": "hotel_login", "code": "123456"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        payload = decode_token(data["access_token"])
        self.assertEqual(payload["role"], "hotel")
        self.assertEqual(payload["hotel_id"], hotel.id)
