from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import Post, Tag
from hotel.models import Hotel
from hotel.serializers.hotel_serializer import CreateHotelSerializer
from core.utils.api_response import success_response, error_response


class TagHotelsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, tag_id):
        if not Tag.objects.filter(id=tag_id).exists():
            return error_response(message="Tag not found", code=404)

        hotels = Hotel.objects.filter(
            Q(tags__id=tag_id)
            | Q(posts__tags__id=tag_id, posts__status=Post.Status.PUBLISHED)
        ).distinct()

        serializer = CreateHotelSerializer(hotels, many=True)
        return success_response(
            message="Hotels fetched successfully",
            data=serializer.data
        )
