from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import Hotel
from ..serializers.hotel_serializer import CreateHotelSerializer
from core.utils.api_response import success_response


class ListHotelsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        hotels = Hotel.objects.all()
        serializer = CreateHotelSerializer(hotels, many=True)
        return success_response(
            message="Hotels fetched successfully",
            data=serializer.data
        )
