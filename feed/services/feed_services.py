from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from post.models import Post


def get_feed(lat,lon,radius_km=10):
    user_location = Point(lon,lat,srid=4326)

    print(user_location)
    posts = (
        Post.objects.filter(
            status=Post.Status.PUBLISHED,
            location__distance_lte=(
                user_location,
                D(km=radius_km)
            )
        )
        .prefetch_related('likes')
        .order_by("composite_score")[:20]
    )
    print(posts)

    return posts

