from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from post.models import Post






def get_explore_page_content(lat,lon,radius_km=20):
    user_location = Point(lon,lat,srid=4326)

    posts = (
        Post.objects.filter(
            status=Post.Status.PUBLISHED,
            location__distance_lte=(
                user_location,
                D(km=radius_km)
            )
        )
        .order_by("-composite_score")[:40]
    )

    return posts

