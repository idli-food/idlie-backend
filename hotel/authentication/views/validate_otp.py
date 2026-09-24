from rest_framework.views import APIView

from core.utils.api_response import success_response, error_response
from otp import services as otp_services
from otp.exceptions import OTPError
from otp.tokens import issue_verification_token


class ValidateOTPView(APIView):

    def post(self, request):

        otp = request.data.get("otp")
        phone_number = request.data.get("phone_number")

        if not otp:
            return error_response(message="OTP not provided")

        try:
            result = otp_services.verify_otp(phone_number, "hotel_signup", otp)
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        verification_token = issue_verification_token(result["phone"], "hotel_signup")

        # Reuses the pre-existing `request_id` response key so the Flutter
        # client's `response['request_id']` parsing keeps working unchanged.
        return success_response(message="OTP verfied", request_id=verification_token)
