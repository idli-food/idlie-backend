from unittest.mock import MagicMock, patch

from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from hotel.models import Hotel

TEST_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


@override_settings(CACHES=TEST_CACHES)
class HotelSignupFlowTests(APITestCase):

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

        patcher = patch("otp.services._twilio_client")
        self.mock_twilio_client = patcher.start()
        self.addCleanup(patcher.stop)

        service = self.mock_twilio_client.return_value.verify.v2.services.return_value
        service.verifications.create.return_value = MagicMock(sid="VEtestsid00000000000000000000000")
        service.verification_checks.create.return_value = MagicMock(status="approved")

    def test_full_signup_flow_creates_verified_hotel(self):
        phone = "+919876543210"

        signup = self.client.post("/hotel/signup/", {"phone_number": phone}, format="json")
        self.assertEqual(signup.status_code, status.HTTP_200_OK)

        validate = self.client.post(
            "/hotel/validate-otp/", {"otp": "123456", "phone_number": phone}, format="json"
        )
        self.assertEqual(validate.status_code, status.HTTP_200_OK)
        request_id = validate.data["request_id"]
        self.assertIsNotNone(request_id)

        create = self.client.post(
            "/hotel/create/",
            {
                "request_id": request_id,
                "phone_number": phone,
                "name": "Test Hotel",
                "address": "123 St",
                "city": "Testville",
                "password": "supersecret",
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Hotel.objects.count(), 1)
        hotel = Hotel.objects.first()
        self.assertTrue(hotel.phone_verified)
        self.assertIsNotNone(hotel.phone_verified_at)

    def test_create_with_missing_request_id_rejected(self):
        create = self.client.post(
            "/hotel/create/",
            {
                "phone_number": "+919876543210",
                "name": "Test Hotel",
                "address": "123 St",
                "city": "Testville",
                "password": "supersecret",
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_with_invalid_request_id_rejected(self):
        create = self.client.post(
            "/hotel/create/",
            {
                "request_id": "not-a-real-token",
                "phone_number": "+919876543210",
                "name": "Test Hotel",
                "address": "123 St",
                "city": "Testville",
                "password": "supersecret",
            },
            format="json",
        )
        self.assertEqual(create.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_full_password_reset_flow(self):
        phone = "+919876543299"
        hotel = Hotel.objects.create(
            name="Existing Hotel", address="1 Rd", city="Town", phone_number=phone
        )
        hotel.set_password("oldpassword")
        hotel.save()

        send = self.client.post(
            "/otp/send/", {"phone": phone, "purpose": "password_reset"}, format="json"
        )
        self.assertEqual(send.status_code, status.HTTP_200_OK)

        verify = self.client.post(
            "/otp/verify/",
            {"phone": phone, "purpose": "password_reset", "code": "123456"},
            format="json",
        )
        self.assertEqual(verify.status_code, status.HTTP_200_OK)
        verification_token = verify.data["data"]["verification_token"]

        reset = self.client.post(
            "/hotel/reset-password/",
            {
                "phone_number": phone,
                "verification_token": verification_token,
                "new_password": "newpassword123",
            },
            format="json",
        )
        self.assertEqual(reset.status_code, status.HTTP_200_OK)

        login_new = self.client.post(
            "/hotel/login/", {"phone_number": phone, "password": "newpassword123"}, format="json"
        )
        self.assertEqual(login_new.status_code, status.HTTP_200_OK)

        login_old = self.client.post(
            "/hotel/login/", {"phone_number": phone, "password": "oldpassword"}, format="json"
        )
        self.assertEqual(login_old.status_code, status.HTTP_400_BAD_REQUEST)
