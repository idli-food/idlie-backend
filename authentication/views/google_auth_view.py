import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import jwt
from django.conf import settings
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.views import APIView

from core.utils.api_response import success_response, error_response
from user.models import User
from user.serivices.user_profile import create_user_profile

from ..jwt.cookies import set_auth_cookies
from ..jwt.jwt_utils import create_access_token, create_refresh_token, decode_token
from ..models import GoogleIdentity
from ..service.OTPservices import OTPServices
from ..service.google_oauth import build_auth_url, exchange_code, fetch_userinfo, verify_id_token
from ..service.ownership import is_phone_number_available

REGISTRATION_TOKEN_LIFETIME = timedelta(minutes=15)


def _frontend_redirect(path, **params):
    url = f"{settings.FRONTEND_URL}{path}"
    if params:
        url = f"{url}?{urlencode(params)}"
    return redirect(url)


def _build_registration_token(sub, email, name, picture):
    now = datetime.now(timezone.utc)
    payload = {
        "type": "google_pending",
        "sub": sub,
        "email": email,
        "name": name,
        "picture": picture,
        "iat": now,
        "exp": now + REGISTRATION_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


class GoogleLoginView(APIView):

    def get(self, request):
        state = secrets.token_urlsafe(32)
        request.session["google_oauth_state"] = state
        return redirect(build_auth_url(state))


class GoogleCallbackView(APIView):

    def get(self, request):
        state = request.GET.get("state")
        stored_state = request.session.pop("google_oauth_state", None)
        if not state or state != stored_state:
            return _frontend_redirect("/login", error="invalid_state")

        code = request.GET.get("code")
        if not code:
            return _frontend_redirect("/login", error="missing_code")

        try:
            token_data = exchange_code(code)
            userinfo = fetch_userinfo(token_data["access_token"])
        except Exception:
            return _frontend_redirect("/login", error="google_auth_failed")

        sub = userinfo.get("sub")
        email = userinfo.get("email")
        if not sub or not email:
            return _frontend_redirect("/login", error="incomplete_profile")

        identity = GoogleIdentity.objects.filter(google_sub=sub).first()
        if identity:
            response = _frontend_redirect("/feed")
            set_auth_cookies(
                response,
                create_access_token(identity.user.id),
                create_refresh_token(identity.user.id),
            )
            return response

        registration_token = _build_registration_token(
            sub, email, userinfo.get("name", ""), userinfo.get("picture", "")
        )
        return _frontend_redirect("/complete-profile", token=registration_token)


class GoogleTokenAuthView(APIView):

    def post(self, request):
        id_token_str = request.data.get("id_token")
        if not id_token_str:
            return error_response(message="id_token is required")

        try:
            payload = verify_id_token(id_token_str)
        except Exception:
            return error_response(message="Invalid Google token", code=status.HTTP_401_UNAUTHORIZED)

        sub = payload.get("sub")
        email = payload.get("email")
        if not sub or not email:
            return error_response(message="Incomplete Google profile")

        identity = GoogleIdentity.objects.filter(google_sub=sub).first()
        if identity:
            user = identity.user
            access = create_access_token(user.id)
            refresh = create_refresh_token(user.id)
            return success_response(
                message="Login successful",
                data={
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "phone_number": user.phone,
                    },
                    "tokens": {
                        "access": access,
                        "refresh": refresh,
                    },
                    "is_new_user": False,
                },
            )

        registration_token = _build_registration_token(
            sub, email, payload.get("name", ""), payload.get("picture", "")
        )
        return success_response(
            message="Profile completion required",
            data={
                "is_new_user": True,
                "registration_token": registration_token,
                "email": email,
                "name": payload.get("name", ""),
                "picture": payload.get("picture", ""),
            },
        )


class GoogleCompleteView(APIView):

    def post(self, request):
        token = request.data.get("token")
        username = request.data.get("username")
        phone = request.data.get("phone")

        if not token or not username or not phone:
            return error_response(message="token, username and phone are required")

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return error_response(message="Registration token expired", code=status.HTTP_401_UNAUTHORIZED)
        except jwt.InvalidTokenError:
            return error_response(message="Invalid registration token", code=status.HTTP_401_UNAUTHORIZED)

        if payload.get("type") != "google_pending":
            return error_response(message="Invalid token type", code=status.HTTP_401_UNAUTHORIZED)

        if GoogleIdentity.objects.filter(google_sub=payload["sub"]).exists():
            return error_response(message="Account already exists", data="login")

        username = username.strip()
        if not username:
            return error_response(message="username is required")
        if User.objects.filter(username=username).exists():
            return error_response(message="username already taken")

        if not OTPServices.validate_phonenumber(phone):
            return error_response(message="invalid phone number pls check", data=phone)

        if not is_phone_number_available(phone):
            return error_response(message="phone number already taken", data="login")

        user = User.objects.create_user(username=username, phone=phone)
        user.email = payload["email"]
        user.set_unusable_password()
        user.save()

        create_user_profile(user)
        profile = user.profile
        profile.name = payload.get("name", "")
        if payload.get("picture"):
            profile.avatar = payload["picture"]
        profile.save()

        GoogleIdentity.objects.create(user=user, google_sub=payload["sub"], email=payload["email"])

        access = create_access_token(user.id)
        refresh = create_refresh_token(user.id)
        response = success_response(
            message="User created successfully",
            code=status.HTTP_201_CREATED,
            data={
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "phone_number": user.phone,
                },
                "tokens": {
                    "access": access,
                    "refresh": refresh,
                },
            },
        )
        set_auth_cookies(response, access, refresh)
        return response
