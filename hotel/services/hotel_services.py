

from hotel.models import Hotel





def get_hotel_id_by_phone_number(phone_number):
    try:
        hotel = Hotel.objects.get(phone_number=phone_number)
        return hotel.id
    except Hotel.DoesNotExist:
        return None


def calculate_profile_completion(hotel):
    fields = [
        hotel.name,
        hotel.phone_number,
        hotel.location,
        hotel.avatar,
    ]

    filled = sum(
        value is not None and value != ""
        for value in fields
    )

    percentage = (filled / len(fields)) * 100

    return percentage