from user.models import User


def is_phone_number_available(phone_number):
    return not User.objects.filter(phone=phone_number).exists()