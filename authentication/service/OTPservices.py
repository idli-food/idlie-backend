

import re


class OTPServices:

    @classmethod
    def validate_phonenumber(cls,phone_number):
        pattern = r"^\+91[6-9]\d{9}$"
        return bool(re.match(pattern, phone_number))
    
    @classmethod
    def generate_opt(cls,phone_number):
        return({
            "otp" : 221180,
            "request_id" : 20
        })
    
    @classmethod
    def validate_OTP(cls,otp):
        original_otp = "221180"

        if otp == original_otp:
            return True
        return False