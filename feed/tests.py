from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from post.models import Post

point = Point(76.4915128566441, 9.144169992692108, srid=4326)

qs = Post.objects.filter(
    location__distance_lte=(point, D(km=10)),
    status="PUBLISHED"
)

print(qs.count())

for p in qs:
    print(p.id, p.location)