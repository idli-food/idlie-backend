from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance

from ..models import Hotel
from ..serializers.nearest_hotel_serializer import (
    NearestHotelRequestSerializer,
    NearestHotelSerializer,
)
from core.utils.api_response import success_response, error_response

NEAREST_HOTEL_RADIUS_M = 5000


class NearestHotelView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NearestHotelRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST
            )

        latitude = serializer.validated_data["latitude"]
        longitude = serializer.validated_data["longitude"]
        user_location = Point(longitude, latitude, srid=4326)

        hotel = Hotel.objects.filter(
            is_active=True,
            location__distance_lte=(user_location, D(m=NEAREST_HOTEL_RADIUS_M))
        ).annotate(
            distance=Distance("location", user_location)
        ).order_by("distance").first()

        if hotel is None:
            return error_response(
                message="No hotel found within radius",
                code=status.HTTP_404_NOT_FOUND
            )
        print(hotel)

        return success_response(
            message="Nearest hotel fetched successfully",
            data=NearestHotelSerializer(hotel).data
        )
