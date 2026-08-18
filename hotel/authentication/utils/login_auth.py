from django.contrib.auth import get_user_model
from django.db.models import Q
from hotel.models import Hotel


def validate_phone_number(phone_number):
    return Hotel.objects.filter(phone_number=phone_number).exists()