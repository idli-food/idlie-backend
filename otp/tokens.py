import secrets

from django.core import signing
from django.core.cache import cache

from .exceptions import InvalidVerificationTokenError

SALT = "otp.verification_token"
TOKEN_MAX_AGE_SECONDS = 600


def _vtoken_key(jti):
    return f"otp:vtoken:{jti}"


def issue_verification_token(phone, purpose):
    jti = secrets.token_urlsafe(16)
    cache.set(_vtoken_key(jti), {"phone": phone, "purpose": purpose}, timeout=TOKEN_MAX_AGE_SECONDS)
    return signing.dumps({"phone": phone, "purpose": purpose, "jti": jti}, salt=SALT)


def consume_verification_token(token, expected_purpose, expected_phone=None):
    if not token:
        raise InvalidVerificationTokenError()

    try:
        payload = signing.loads(token, salt=SALT, max_age=TOKEN_MAX_AGE_SECONDS)
    except signing.BadSignature:
        raise InvalidVerificationTokenError()

    if payload.get("purpose") != expected_purpose:
        raise InvalidVerificationTokenError()

    if expected_phone is not None and payload.get("phone") != expected_phone:
        raise InvalidVerificationTokenError()

    jti = payload.get("jti")
    key = _vtoken_key(jti)
    if cache.get(key) is None:
        raise InvalidVerificationTokenError()

    cache.delete(key)
    return payload["phone"]
