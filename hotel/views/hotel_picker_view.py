from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import Hotel
from core.utils.api_response import success_response


class HotelPickerView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hotels = Hotel.objects.order_by("name").values("id", "name", "address", "city")

        return success_response(
            message="Hotels fetched successfully",
            data=list(hotels)
        )
