from django.contrib.auth import get_user_model
from django.db.models import Q
from user.models import User


def authenticate_user(identifier, password):
    """
    identifier can be:
    - username
    - phone number
    """

    try:
        user = User.objects.get(
            Q(username=identifier) |
            Q(phone=identifier)
        )
    except User.DoesNotExist:
        return None

    if user.check_password(password):
        return user

    return None