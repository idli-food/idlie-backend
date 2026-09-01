from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import Q, Case, When, Value, IntegerField
from post.models import Post


def get_posts_by_hotel_address(query):
    """Published posts whose tagged hotel's address/city matches `query`."""
    return Post.objects.filter(
        status=Post.Status.PUBLISHED,
        hotel__isnull=False,
    ).filter(
        Q(hotel__address__icontains=query) | Q(hotel__city__icontains=query)
    )


def get_explore_page_content(lat=None, lon=None, radius_km=20, query=None):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED)

    if lat is not None and lon is not None:
        user_location = Point(lon, lat, srid=4326)
        posts = posts.filter(
            location__distance_lte=(user_location, D(km=radius_km))
        )

    if query:
        address_post_ids = get_posts_by_hotel_address(query).values_list("id", flat=True)
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(id__in=address_post_ids)
        ).annotate(
            title_hit=Case(
                When(title__icontains=query, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            )
        ).order_by("-title_hit", "-avg_rating", "-composite_score")[:40]
    else:
        posts = posts.order_by("-composite_score")[:40]

    return posts


def group_posts_by_rating(posts):
    """Ordered dict of "5".."0" -> list of posts, bucket = round(avg_rating)."""
    buckets = {str(n): [] for n in range(5, -1, -1)}
    for post in posts:
        b = max(0, min(5, round(post.avg_rating or 0)))
        buckets[str(b)].append(post)
    return buckets
