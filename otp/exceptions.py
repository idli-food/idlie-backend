from rest_framework import status


class OTPError(Exception):
    """Base class for otp app errors. `code` is the HTTP status to respond with."""

    code = status.HTTP_400_BAD_REQUEST
    message = "Something went wrong"

    def __init__(self, message=None, **extra):
        self.message = message or self.message
        self.extra = extra
        super().__init__(self.message)


class InvalidPhoneError(OTPError):
    code = status.HTTP_400_BAD_REQUEST
    message = "Invalid phone number, please check and try again"


class PhoneAlreadyRegisteredError(OTPError):
    code = status.HTTP_400_BAD_REQUEST
    message = "Phone number already registered"


class CooldownError(OTPError):
    code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Please wait before requesting another code"


class CodeExpiredError(OTPError):
    code = status.HTTP_410_GONE
    message = "Code expired or already used, please request a new one"


class WrongCodeError(OTPError):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Incorrect code"


class MaxAttemptsError(OTPError):
    code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many incorrect attempts, please request a new code"


class MaxSendsError(OTPError):
    code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many requests, please try again later"


class FraudBlockError(OTPError):
    code = status.HTTP_403_FORBIDDEN
    message = "This phone number cannot be verified right now"


class RateLimitedError(OTPError):
    code = status.HTTP_429_TOO_MANY_REQUESTS
    message = "Too many requests, please try again later"


class InvalidVerificationTokenError(OTPError):
    code = status.HTTP_401_UNAUTHORIZED
    message = "Invalid or expired verification, please verify again"
