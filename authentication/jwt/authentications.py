import jwt

from django.conf import settings
from user.models import User
from hotel.models import Hotel

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed



class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if auth_header:
            prefix, _, token = auth_header.partition(" ")
            if prefix.lower() != "bearer" or not token:
                raise AuthenticationFailed("Invalid token prefix")
        else:
            token = request.COOKIES.get("access_token")
            if not token:
                return None

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"]
            )

            if payload["type"] != "access":
                raise AuthenticationFailed("Invalid token type")



            if payload["role"] == "hotel":
                principal = Hotel.objects.get(id=payload["hotel_id"])

            elif payload["role"] == "user":
                principal = User.objects.get(id=payload["user_id"])
            else:
                raise AuthenticationFailed("Invalid role in token")


            return (principal, token)

        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token expired")

        except jwt.DecodeError:
            raise AuthenticationFailed("Invalid token")

        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
        except Hotel.DoesNotExist:
            raise AuthenticationFailed("User not found")
        except Exception as e:
            raise AuthenticationFailed(str(e))