
from twilio.rest import Client
from django.conf import settings

import re



client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


class OTPServices:

    @classmethod
    def validate_phonenumber(cls,phone_number):
        pattern = r"^\+91[6-9]\d{9}$"
        return bool(re.match(pattern, phone_number))
    
    @classmethod
    def generate_opt(cls,phone_number):
        verification = client.verify.v2.services(
            settings.TWILIO_VERIFY_SERVICE_SID
        ).verifications.create(to=phone_number, channel="sms")
        return {
            "status": verification.status,
        }
    
    @classmethod
    def validate_OTP(cls,otp):
        original_otp = "221180"

        if otp == original_otp:
            return True
        return False