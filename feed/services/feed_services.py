from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from post.models import Post
from hotel.models import Hotel

FEED_RADIUS_KM = 30


def get_hotel_location_link(hotel_id):
    if not hotel_id:
        return None
    return (
        Hotel.objects.filter(pk=hotel_id)
        .values_list("location_link", flat=True)
        .first()
    )


def get_feed_by_post_rating(lat=None, lon=None, limit=20):
    posts = (
        Post.objects.filter(
            status=Post.Status.PUBLISHED,
            hotel__isnull=False,
        )
        .prefetch_related("likes", "saved", "rating")
        .order_by("-avg_rating", "-rating_count", "-created_at")
    )

    if lat is not None and lon is not None:
        user_location = Point(lon, lat, srid=4326)
        return posts.filter(
            location__distance_lte=(user_location, D(km=FEED_RADIUS_KM))
        )

    return posts[:limit]

