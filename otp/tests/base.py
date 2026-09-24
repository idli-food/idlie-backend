from unittest.mock import MagicMock, patch

from django.test import override_settings
from rest_framework.test import APITestCase

TEST_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


@override_settings(CACHES=TEST_CACHES)
class OtpAPITestCase(APITestCase):
    """Base test case: uses an in-process cache (no real Redis needed) and
    mocks the Twilio client so no real SMS is ever sent."""

    def setUp(self):
        super().setUp()
        from django.core.cache import cache

        cache.clear()

        patcher = patch("otp.services._twilio_client")
        self.mock_twilio_client = patcher.start()
        self.addCleanup(patcher.stop)

        self.mock_verifications = MagicMock()
        self.mock_verification_checks = MagicMock()
        service = self.mock_twilio_client.return_value.verify.v2.services.return_value
        service.verifications = self.mock_verifications
        service.verification_checks = self.mock_verification_checks

        self.mock_verifications.create.return_value = MagicMock(sid="VEtestsid00000000000000000000000")
