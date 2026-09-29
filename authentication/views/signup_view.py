from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView

from core.utils.api_response import error_response, success_response
from otp import services as otp_services
from otp.exceptions import InvalidPhoneError, OTPError
from otp.tokens import consume_verification_token
from user.models import User
from user.serivices.user_profile import create_user_profile

from ..jwt.cookies import set_auth_cookies
from ..jwt.jwt_utils import create_access_token, create_refresh_token


class SignupView(APIView):

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        phone = request.data.get("phone")
        verification_token = request.data.get("verification_token")

        if not username or not phone or not verification_token:
            return error_response(message="username, phone and verification_token are required")

        try:
            phone = otp_services.normalize_phone(phone)
        except InvalidPhoneError:
            return error_response(message="invalid phone number pls check", data=phone)

        if User.objects.filter(username=username).exists():
            return error_response(message="username already taken")
        if User.objects.filter(phone=phone).exists():
            return error_response(message="phone number already taken", data="login")

        try:
            consume_verification_token(verification_token, expected_purpose="user_auth", expected_phone=phone)
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        user = User.objects.create_user(username=username, phone=phone)
        user.set_unusable_password()
        user.phone_verified = True
        user.phone_verified_at = timezone.now()
        user.save()

        create_user_profile(user)

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        response = success_response(
            message="User created successfully",
            code=status.HTTP_201_CREATED,
            data={
                "user": {"id": user.id, "username": user.username, "phone_number": user.phone},
                "tokens": {"access": access, "refresh": refresh},
            },
        )
        set_auth_cookies(response, access, refresh)
        return response
