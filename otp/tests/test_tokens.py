from django.test import TestCase, override_settings

from otp.exceptions import InvalidVerificationTokenError
from otp.tokens import consume_verification_token, issue_verification_token

TEST_CACHES = {
    "default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}
}


@override_settings(CACHES=TEST_CACHES)
class VerificationTokenTests(TestCase):

    def setUp(self):
        from django.core.cache import cache

        cache.clear()

    def test_round_trip_succeeds(self):
        token = issue_verification_token("+919876543210", "hotel_signup")
        phone = consume_verification_token(token, expected_purpose="hotel_signup")
        self.assertEqual(phone, "+919876543210")

    def test_second_consume_fails(self):
        token = issue_verification_token("+919876543210", "hotel_signup")
        consume_verification_token(token, expected_purpose="hotel_signup")
        with self.assertRaises(InvalidVerificationTokenError):
            consume_verification_token(token, expected_purpose="hotel_signup")

    def test_wrong_purpose_fails(self):
        token = issue_verification_token("+919876543210", "hotel_signup")
        with self.assertRaises(InvalidVerificationTokenError):
            consume_verification_token(token, expected_purpose="user_signup")

    def test_wrong_phone_fails(self):
        token = issue_verification_token("+919876543210", "hotel_signup")
        with self.assertRaises(InvalidVerificationTokenError):
            consume_verification_token(
                token, expected_purpose="hotel_signup", expected_phone="+919876543299"
            )

    def test_tampered_token_fails(self):
        token = issue_verification_token("+919876543210", "hotel_signup")
        with self.assertRaises(InvalidVerificationTokenError):
            consume_verification_token(token + "tampered", expected_purpose="hotel_signup")

    def test_empty_token_fails(self):
        with self.assertRaises(InvalidVerificationTokenError):
            consume_verification_token("", expected_purpose="hotel_signup")
