import logging

import phonenumbers
from django.conf import settings
from django.core.cache import cache
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from hotel.models import Hotel
from user.models import User

from .exceptions import (
    CodeExpiredError,
    CooldownError,
    FraudBlockError,
    InvalidPhoneError,
    MaxAttemptsError,
    MaxSendsError,
    PhoneAlreadyRegisteredError,
    RateLimitedError,
    WrongCodeError,
)

logger = logging.getLogger("otp")

PURPOSES = ("hotel_signup", "hotel_login", "user_signup", "password_reset")

COOLDOWN_SECONDS = 30
PENDING_TTL_SECONDS = 600

_PURPOSE_SID_SETTING = {
    "hotel_signup": "TWILIO_VERIFY_SID_HOTEL_SIGNUP",
    "hotel_login": "TWILIO_VERIFY_SID_HOTEL_LOGIN",
    "user_signup": "TWILIO_VERIFY_SID_USER_SIGNUP",
    "password_reset": "TWILIO_VERIFY_SID_PASSWORD_RESET",
}

_client = None


def _twilio_client():
    global _client
    if _client is None:
        _client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    return _client


def _verify_service_sid(purpose):
    return getattr(settings, _PURPOSE_SID_SETTING[purpose], None) or settings.TWILIO_VERIFY_SERVICE_SID


def mask_phone(phone):
    if not phone or len(phone) < 4:
        return "***"
    return f"{phone[:3]}{'*' * max(len(phone) - 7, 0)}{phone[-4:]}"


def normalize_phone(raw_phone):
    if not raw_phone:
        raise InvalidPhoneError()
    try:
        parsed = phonenumbers.parse(raw_phone, "IN")
    except phonenumbers.NumberParseException:
        raise InvalidPhoneError()

    if not phonenumbers.is_valid_number(parsed):
        raise InvalidPhoneError()

    number_type = phonenumbers.number_type(parsed)
    if number_type not in (
        phonenumbers.PhoneNumberType.MOBILE,
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE,
    ):
        raise InvalidPhoneError(message="Please provide a mobile number")

    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def _cooldown_key(phone, purpose):
    return f"otp:cooldown:{purpose}:{phone}"


def _pending_key(phone, purpose):
    return f"otp:pending:{purpose}:{phone}"


def check_cooldown(phone, purpose):
    key = _cooldown_key(phone, purpose)
    allowed_at = cache.get(key)
    now = _now().timestamp()
    if allowed_at is not None and now < allowed_at:
        raise CooldownError(seconds_remaining=int(allowed_at - now))
    cache.set(key, now + COOLDOWN_SECONDS, timeout=COOLDOWN_SECONDS)


def _own_phone(account):
    if isinstance(account, Hotel):
        return account.phone_number
    if isinstance(account, User):
        return account.phone
    return None


def _is_own_phone(account, phone):
    return account is not None and _own_phone(account) == phone


def purpose_precondition(phone, purpose, requesting_account=None):
    """Returns True if Twilio should actually be called, False for a silent
    anti-enumeration no-op (send endpoint should still report generic success)."""

    if purpose == "hotel_signup":
        exists = Hotel.objects.filter(phone_number=phone).exclude(
            pk=requesting_account.pk if isinstance(requesting_account, Hotel) else None
        ).exists()
        if exists and not _is_own_phone(requesting_account, phone):
            raise PhoneAlreadyRegisteredError(message="Phone number already registered")
        return True

    if purpose == "user_signup":
        exists = User.objects.filter(phone=phone).exclude(
            pk=requesting_account.pk if isinstance(requesting_account, User) else None
        ).exists()
        if exists and not _is_own_phone(requesting_account, phone):
            raise PhoneAlreadyRegisteredError(message="Phone number already registered")
        return True

    if purpose in ("hotel_login", "password_reset"):
        return Hotel.objects.filter(phone_number=phone).exists()

    raise InvalidPhoneError(message="Unsupported purpose")


def send_otp(phone_raw, purpose, requesting_account=None):
    phone = normalize_phone(phone_raw)
    check_cooldown(phone, purpose)

    should_send = purpose_precondition(phone, purpose, requesting_account=requesting_account)
    if not should_send:
        logger.info("otp send skipped (anti-enumeration) purpose=%s phone=%s", purpose, mask_phone(phone))
        return phone

    sid = _verify_service_sid(purpose)
    verification = _twilio_client().verify.v2.services(sid).verifications.create(to=phone, channel="sms")
    cache.set(_pending_key(phone, purpose), verification.sid, timeout=PENDING_TTL_SECONDS)
    logger.info("otp sent purpose=%s phone=%s", purpose, mask_phone(phone))
    return phone


_TWILIO_ERROR_MAP = {
    60202: MaxAttemptsError,
    60203: MaxSendsError,
    60200: InvalidPhoneError,
    60410: FraudBlockError,
    20429: RateLimitedError,
}


def verify_otp(phone_raw, purpose, code, requesting_account=None):
    phone = normalize_phone(phone_raw)
    pending_sid = cache.get(_pending_key(phone, purpose))
    if not pending_sid:
        raise CodeExpiredError()

    sid = _verify_service_sid(purpose)
    try:
        check = _twilio_client().verify.v2.services(sid).verification_checks.create(to=phone, code=code)
    except TwilioRestException as exc:
        if exc.status == 404:
            raise CodeExpiredError()
        error_cls = _TWILIO_ERROR_MAP.get(exc.code)
        if error_cls:
            raise error_cls()
        logger.warning("unmapped twilio error purpose=%s phone=%s code=%s", purpose, mask_phone(phone), exc.code)
        raise

    if check.status != "approved":
        raise WrongCodeError()

    cache.delete(_pending_key(phone, purpose))
    logger.info("otp verified purpose=%s phone=%s", purpose, mask_phone(phone))

    if _is_own_phone(requesting_account, phone):
        requesting_account.phone_verified = True
        requesting_account.phone_verified_at = _now()
        requesting_account.save(update_fields=["phone_verified", "phone_verified_at"])
        return {"kind": "self_reverified"}

    return {"kind": "otp_verified", "phone": phone}


def _now():
    from django.utils import timezone

    return timezone.now()
