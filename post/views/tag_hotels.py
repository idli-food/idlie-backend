from django.db.models import Prefetch, Q
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ..models import Post, Tag
from hotel.models import Hotel
from hotel.serializers.hotel_serializer import CreateHotelSerializer
from core.utils.api_response import success_response, error_response


class TagHotelsView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, tag_id):
        if not Tag.objects.filter(id=tag_id).exists():
            return error_response(message="Tag not found", code=404)

        hotels = Hotel.objects.filter(
            Q(tags__id=tag_id)
            | Q(posts__tags__id=tag_id, posts__status=Post.Status.PUBLISHED)
        ).distinct()

        hotels = list(hotels.prefetch_related(Prefetch(
            "posts",
            queryset=Post.objects.filter(status=Post.Status.PUBLISHED)
            .prefetch_related("media")
            .order_by("-created_at")[:3],
            to_attr="latest_posts",
        )))

        data = CreateHotelSerializer(hotels, many=True).data
        for item, hotel in zip(data, hotels):
            item["thumbnails"] = [
                post.media.all()[0].thumbnail_url
                for post in hotel.latest_posts
                if post.media.all()
            ]

        return success_response(
            message="Hotels fetched successfully",
            data=data
        )
