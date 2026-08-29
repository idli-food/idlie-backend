from django.conf import settings

ACCESS_COOKIE = "access_token"
REFRESH_COOKIE = "refresh_token"


def set_auth_cookies(response, access, refresh=None):
    samesite = settings.AUTH_COOKIE_SAMESITE
    # Browsers reject SameSite=None unless the cookie is also Secure.
    secure = settings.AUTH_COOKIE_SECURE or samesite == "None"
    response.set_cookie(
        ACCESS_COOKIE, access,
        max_age=int(settings.ACCESS_TOKEN_LIFETIME.total_seconds()),
        httponly=True, secure=secure, samesite=samesite, path="/",
    )
    if refresh is not None:
        response.set_cookie(
            REFRESH_COOKIE, refresh,
            max_age=int(settings.REFRESH_TOKEN_LIFETIME.total_seconds()),
            httponly=True, secure=secure, samesite=samesite, path="/",
        )
    return response


def clear_auth_cookies(response):
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")
    return response
