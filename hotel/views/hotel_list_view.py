from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Prefetch, Q
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from ..models import Hotel
from post.models import Post
from ..serializers.hotel_serializer import CreateHotelSerializer
from core.utils.api_response import success_response, error_response

HOTEL_LIST_RADIUS_KM = 10


class ListHotelsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        try:
            lat = float(lat) if lat is not None else None
            lon = float(lon) if lon is not None else None
        except ValueError:
            return error_response(message="Invalid lat or lon")

        hotels = Hotel.objects.filter(posts__status=Post.Status.PUBLISHED).distinct()

        query = request.GET.get("q", "").strip()
        if query:
            hotels = hotels.filter(
                Q(name__icontains=query)
                | Q(address__icontains=query)
                | Q(city__icontains=query)
            )

        if lat is not None and lon is not None:
            user_location = Point(lon, lat, srid=4326)
            hotels = hotels.filter(
                location__distance_lte=(user_location, D(km=HOTEL_LIST_RADIUS_KM))
            )

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
