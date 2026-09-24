from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from authentication.jwt.authentications import JWTAuthentication
from core.utils.api_response import error_response, success_response
from hotel.authentication.services.jwt.jwt_utils import (
    create_access_token as create_hotel_access_token,
    create_refresh_token as create_hotel_refresh_token,
)
from hotel.models import Hotel
from user.models import User

from .exceptions import CooldownError, OTPError
from .serializers import SendOtpSerializer, VerifyOtpSerializer
from .tokens import issue_verification_token
from . import services


def _requesting_account(request):
    if isinstance(request.user, (Hotel, User)):
        return request.user
    return None


class SendOtpView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_send"

    def post(self, request):
        serializer = SendOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid request", errors=serializer.errors)

        try:
            services.send_otp(
                serializer.validated_data["phone"],
                serializer.validated_data["purpose"],
                requesting_account=_requesting_account(request),
            )
        except CooldownError as exc:
            return error_response(
                message=exc.message,
                code=exc.code,
                data={"seconds_remaining": exc.extra.get("seconds_remaining")},
            )
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        return success_response(message="OTP sent")


class VerifyOtpView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "otp_verify"

    def post(self, request):
        serializer = VerifyOtpSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(message="Invalid request", errors=serializer.errors)

        phone = serializer.validated_data["phone"]
        purpose = serializer.validated_data["purpose"]
        code = serializer.validated_data["code"]

        try:
            result = services.verify_otp(
                phone, purpose, code, requesting_account=_requesting_account(request)
            )
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        if result["kind"] == "self_reverified":
            return success_response(message="Phone verified")

        verified_phone = result["phone"]

        if purpose == "hotel_login":
            try:
                hotel = Hotel.objects.get(phone_number=verified_phone)
            except Hotel.DoesNotExist:
                return error_response(message="Invalid or expired verification", code=401)
            access_token = create_hotel_access_token(hotel.id)
            refresh_token = create_hotel_refresh_token(hotel.id)
            return success_response(
                message="Login successful",
                data={
                    "phone_number": hotel.phone_number,
                    "id": hotel.id,
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            )

        token = issue_verification_token(verified_phone, purpose)
        return success_response(message="OTP verified", data={"verification_token": token})
