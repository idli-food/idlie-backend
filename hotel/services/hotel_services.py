

from hotel.models import Hotel





def get_hotel_id_by_phone_number(phone_number):
    try:
        hotel = Hotel.objects.get(phone_number=phone_number)
        return hotel.id
    except Hotel.DoesNotExist:
        return None