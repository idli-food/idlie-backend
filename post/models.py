from django.db import models
from django.contrib.gis.db import models as gis_models
from foodspot.models import FoodSpot
from user.models import User


class Post(models.Model):
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'


    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    food_spot = models.ForeignKey(
        FoodSpot,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts'
    )
    foodspot_tag = models.CharField(blank=True,null=False)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices
    )

    raw_s3_key = models.CharField(max_length=500)
    media_url = models.URLField()
    thumbnail_url = models.URLField(blank=True)
    is_proccessed = models.BooleanField(default=False)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    )

    like_count = models.PositiveIntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    composite_score = models.FloatField(default=0.0)

    # Optional geolocation for the post itself
    location = gis_models.PointField(geography=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title