import jwt
from datetime import datetime,timedelta,timezone
from django.conf import settings



def create_access_token(user_id):

    payload = {
        "user_id" : user_id,
        "type" : "access",
        "role" : "user",
        "exp" : datetime.now(timezone.utc) + settings.ACCESS_TOKEN_LIFETIME,
        "iat" : datetime.now(timezone.utc),
    }

    return jwt.encode(payload,settings.JWT_SECRET,algorithm="HS256")


def create_refresh_token(user_id):

    payload = {
        "user_id" : user_id,
        "type" : "refresh",
        "role" : "user",
        "exp": datetime.now(timezone.utc) + settings.REFRESH_TOKEN_LIFETIME,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])