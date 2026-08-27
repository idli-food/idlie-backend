from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Avg
from post.models import Post
from hotel.models import Hotel


def get_hotel_location_link(hotel_id):
    if not hotel_id:
        return None
    return (
        Hotel.objects.filter(pk=hotel_id)
        .values_list("location_link", flat=True)
        .first()
    )


def get_feed_by_hotel_rating(limit=20):
    posts = (
        Post.objects.filter(
            status=Post.Status.PUBLISHED,
            hotel__isnull=False,
        )
        .annotate(hotel_avg_rating=Avg("hotel__ratings__rating_count"))
        .prefetch_related("likes")
        .order_by("-hotel_avg_rating")[:limit]
    )
    return posts


# def get_feed(lat,lon,radius_km=30):
#     user_location = Point(lon,lat,srid=4326)

#     print(user_location)
#     posts = (
#         Post.objects.filter(
#             status=Post.Status.PUBLISHED,
#             location__distance_lte=(
#                 user_location,
#                 D(km=radius_km)
#             )
#         )
#         .prefetch_related('likes')
#         .order_by("composite_score")[:20]
#     )
#     return posts

