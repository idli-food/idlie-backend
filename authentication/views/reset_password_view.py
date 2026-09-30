from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import APIView

from core.utils.api_response import error_response, success_response
from otp import services as otp_services
from otp.exceptions import InvalidPhoneError, OTPError
from otp.tokens import consume_verification_token
from user.models import User


class ResetPasswordView(APIView):
    authentication_classes = []

    def post(self, request):
        phone = request.data.get("phone")
        verification_token = request.data.get("verification_token")
        new_password = request.data.get("new_password")

        if not phone or not verification_token or not new_password:
            return error_response(message="phone, verification_token and new_password are required")

        try:
            phone = otp_services.normalize_phone(phone)
        except InvalidPhoneError:
            return error_response(message="invalid phone number pls check", data=phone)

        user = User.objects.filter(phone=phone).first()
        if user is None:
            return error_response(message="Invalid or expired verification", code=401)

        try:
            validate_password(new_password, user)
        except ValidationError as exc:
            return error_response(message=" ".join(exc.messages))

        try:
            consume_verification_token(verification_token, expected_purpose="user_password_reset", expected_phone=phone)
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        user.set_password(new_password)
        user.save(update_fields=["password"])
        return success_response(message="Password reset successful")
