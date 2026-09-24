from rest_framework.views import APIView

from core.utils.api_response import success_response, error_response
from otp import services as otp_services
from otp.exceptions import OTPError


class SignupView(APIView):

    def post(self, request):

        phone_number = request.data.get("phone_number")

        try:
            otp_services.send_otp(phone_number, "hotel_signup")
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        return success_response(message="otp send")
