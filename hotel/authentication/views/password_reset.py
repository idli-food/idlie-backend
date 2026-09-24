from rest_framework.views import APIView

from core.utils.api_response import success_response, error_response
from hotel.models import Hotel
from otp import services as otp_services
from otp.exceptions import InvalidPhoneError, OTPError
from otp.tokens import consume_verification_token


class HotelResetPasswordView(APIView):

    def post(self, request):
        phone_number = request.data.get("phone_number")
        verification_token = request.data.get("verification_token")
        new_password = request.data.get("new_password")

        if not phone_number or not verification_token or not new_password:
            return error_response(message="phone_number, verification_token and new_password are required")

        if len(new_password) < 6:
            return error_response(message="Password must be at least 6 characters")

        try:
            phone_number = otp_services.normalize_phone(phone_number)
        except InvalidPhoneError:
            return error_response(message="invalid phone number pls check", data=phone_number)

        try:
            consume_verification_token(
                verification_token, expected_purpose="password_reset", expected_phone=phone_number
            )
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        try:
            hotel = Hotel.objects.get(phone_number=phone_number)
        except Hotel.DoesNotExist:
            return error_response(message="Invalid or expired verification", code=401)

        hotel.set_password(new_password)
        hotel.save()

        return success_response(message="Password reset successful")
