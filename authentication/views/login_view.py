from rest_framework.permissions import AllowAny
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from core.utils.api_response import error_response, success_response
from otp import services as otp_services
from otp.exceptions import InvalidPhoneError
from user.models import User

from ..jwt.cookies import set_auth_cookies
from ..jwt.jwt_utils import create_access_token, create_refresh_token


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        identifier = (request.data.get("identifier") or "").strip()
        password = request.data.get("password") or ""

        if not identifier or not password:
            return error_response(message="identifier and password are required")

        user = User.objects.filter(username=identifier).first()
        if user is None:
            try:
                phone = otp_services.normalize_phone(identifier)
            except InvalidPhoneError:
                phone = None
            if phone:
                user = User.objects.filter(phone=phone).first()

        if user is None or not user.check_password(password):
            return error_response(message="Invalid credentials", code=401)

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        response = success_response(
            message="Login successful",
            data={
                "user": {"id": user.id, "username": user.username, "phone_number": user.phone},
                "tokens": {"access": access, "refresh": refresh},
            },
        )
        set_auth_cookies(response, access, refresh)
        return response
