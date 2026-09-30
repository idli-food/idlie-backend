from unittest.mock import MagicMock

from rest_framework import status
from twilio.base.exceptions import TwilioRestException

from authentication.jwt.jwt_utils import decode_token
from hotel.models import Hotel
from user.models import User

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


class UserAuthTests(OtpAPITestCase):

    def _verify(self, phone):
        self.client.post(SEND_URL, {"phone": phone, "purpose": "user_auth"}, format="json")
        self.mock_verification_checks.create.return_value = MagicMock(status="approved")
        return self.client.post(
            VERIFY_URL, {"phone": phone, "purpose": "user_auth", "code": "123456"}, format="json"
        )

    def test_new_phone_gets_verification_token(self):
        response = self._verify("+919876543210")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["data"]["is_new_user"])
        self.assertIn("verification_token", response.data["data"])

    def test_existing_phone_is_told_user_exists(self):
        User.objects.create_user(username="arjun", phone="+919876543210")
        response = self._verify("+919876543210")
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_signup_creates_user_with_valid_token(self):
        token = self._verify("+919876543210").data["data"]["verification_token"]
        response = self.client.post(
            "/auth/signup/",
            {"username": "arjun", "phone": "+919876543210", "verification_token": token, "password": "S3cure-pass!x"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="arjun")
        self.assertTrue(user.phone_verified)
        self.assertTrue(user.check_password("S3cure-pass!x"))
        self.assertIn("access_token", response.cookies)

    def test_signup_rejects_taken_username_and_reused_token(self):
        User.objects.create_user(username="taken", phone="+919876543299")
        token = self._verify("+919876543210").data["data"]["verification_token"]
        payload = {"username": "taken", "phone": "+919876543210", "verification_token": token, "password": "S3cure-pass!x"}
        self.assertEqual(self.client.post("/auth/signup/", payload, format="json").status_code, 400)
        payload["username"] = "fresh"
        self.assertEqual(self.client.post("/auth/signup/", payload, format="json").status_code, 201)
        payload["username"] = "fresh2"
        self.assertNotEqual(self.client.post("/auth/signup/", payload, format="json").status_code, 201)


class PasswordLoginTests(OtpAPITestCase):

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(username="arjun", phone="+919876543210")
        self.user.set_password("S3cure-pass!x")
        self.user.save()

    def test_login_by_username_and_phone(self):
        for identifier in ("arjun", "9876543210", "+919876543210"):
            response = self.client.post(
                "/auth/login/", {"identifier": identifier, "password": "S3cure-pass!x"}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK, identifier)
            self.assertIn("access", response.data["data"]["tokens"])
            self.assertIn("access_token", response.cookies)

    def test_wrong_password_and_unknown_user_rejected(self):
        for identifier, password in (("arjun", "nope"), ("ghost", "S3cure-pass!x")):
            response = self.client.post(
                "/auth/login/", {"identifier": identifier, "password": password}, format="json"
            )
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unusable_password_cannot_log_in(self):
        User.objects.create_user(username="nopass", phone="+919876543211")
        response = self.client.post(
            "/auth/login/", {"identifier": "nopass", "password": "anything"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_forgot_password_flow(self):
        phone = "+919876543210"
        self.client.post(SEND_URL, {"phone": phone, "purpose": "user_password_reset"}, format="json")
        self.mock_verification_checks.create.return_value = MagicMock(status="approved")
        verify = self.client.post(
            VERIFY_URL, {"phone": phone, "purpose": "user_password_reset", "code": "123456"}, format="json"
        )
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        token = verify.data["data"]["verification_token"]

        payload = {"phone": phone, "verification_token": token, "new_password": "N3w-pass-word!"}
        self.assertEqual(self.client.post("/auth/reset-password/", payload, format="json").status_code, 200)
        self.assertEqual(self.client.post("/auth/reset-password/", payload, format="json").status_code, 401)

        login = self.client.post(
            "/auth/login/", {"identifier": "arjun", "password": "N3w-pass-word!"}, format="json"
        )
        self.assertEqual(login.status_code, status.HTTP_200_OK)
