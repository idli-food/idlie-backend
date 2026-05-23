import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
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
    is_proccessed = models.BooleanField(default=False)
    thumbnail_url = models.URLField(max_length=2000,blank=True,null=True,default="http://125.0.0.00")
    media_url = models.URLField(max_length=2000,blank=True,null=True,default="http://125.0.0.00")

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
    




class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_post_like'
            )
        ]

class Ratings(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='rating'
    )
    stars = models.SmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_post_rating'
            )
        ]

class Comments(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    created_at = models.DateTimeField(auto_now_add=True)


class Saved(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='saved'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'post'],
                name='unique_user_post_saved'
            )
        ]