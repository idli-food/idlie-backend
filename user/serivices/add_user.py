# services/add_user.py

from django.db import transaction
from rest_framework.exceptions import ValidationError

from ..serializers.user import AddUserSerializer


def create_user(user_data: dict):

    print(user_data)
    if not user_data:
        raise ValidationError({
            "message": "User data is required"
        })

    serializer = AddUserSerializer(data=user_data)

    serializer.is_valid(raise_exception=True)

    with transaction.atomic():
        user = serializer.save()

    return user