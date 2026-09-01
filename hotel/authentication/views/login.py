from rest_framework.views import APIView

from core.utils.api_response import success_response, error_response
from hotel.models import Hotel
from ...authentication.services.jwt.jwt_utils import create_access_token, create_refresh_token


class HotelLoginView(APIView):

    def post(self, request):

        phone_number = request.data.get("phone_number")
        password = request.data.get("password")

        if not phone_number or not password:
            return error_response(message="phone_number and password are required")

        try:
            hotel = Hotel.objects.get(phone_number=phone_number)
        except Hotel.DoesNotExist:
            return error_response(message="Invalid credentials")

        if not hotel.check_password(password):
            return error_response(message="Invalid credentials")

        access_token = create_access_token(hotel.id)
        refresh_token = create_refresh_token(hotel.id)

        return success_response(
            message="Login successful",
            data={
                "phone_number": phone_number,
                "id": hotel.id,
                "access_token": access_token,
                "refresh_token": refresh_token,
            },
        )
