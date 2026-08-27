from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Avg
from post.models import Post


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

