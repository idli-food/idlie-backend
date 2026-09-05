import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.core.validators import MinValueValidator, MaxValueValidator
from user.models import User
from hotel.models import Hotel


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
    )

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='posts',
        null=True,
        blank=True,
    )

    description = models.TextField(blank=True)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT
    ) 

    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveBigIntegerField(default=0)
    avg_rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    composite_score = models.FloatField(default=0.0)

    # Optional geolocation for the post itself
    location = gis_models.PointField(geography=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False)
                    | models.Q(hotel__isnull=False)
                ),
                name='post_has_user_or_hotel',
            )
        ]

    @property
    def author(self):
        return self.user or self.hotel

    def __str__(self):
        return f"Post {self.id}"


class PostMedia(models.Model):
    class ContentType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'

    class Category(models.TextChoices):
        INSTANT = 'instant', 'Instant'
        VIDEO = 'video', 'Video'
        PHOTOS = 'photos', 'Photos'

    class UploadStatus(models.TextChoices):
        PROCESSING = "processing"
        UPLOADED = "uploaded"
        FAILED = "failed"

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media'
    )

    content_type = models.CharField(
        max_length=10,
        choices=ContentType.choices
    )

    position = models.PositiveIntegerField(default=0)

    media_url = models.URLField(max_length=2000, blank=True, null=True, default="http://125.0.0.00")
    media_key = models.CharField(max_length=500)
    is_processed = models.BooleanField(default=False)
    thumbnail_url = models.URLField(max_length=2000, blank=True, null=True, default="http://125.0.0.00")

    category = models.CharField(
        max_length=10,
        choices=Category.choices
    )

    upload_status = models.CharField(
        max_length=10,
        choices=UploadStatus.choices,
        default=UploadStatus.PROCESSING
    )

    class Meta:
        ordering = ['position']

    def __str__(self):
        return f"{self.post_id} media #{self.position}"


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

class PostRating(models.Model):
    class Category(models.TextChoices):
        FOOD = 'food', 'Food'
        SERVICE = 'service', 'Service'
        CLEANLINESS = 'cleanliness', 'Cleanliness'
        VALUE = 'value', 'Value'

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='post_ratings'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices
    )
    score = models.SmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5)
        ]
    )
    review = models.CharField(max_length=100, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['post', 'category'],
                name='unique_post_category_rating'
            )
        ]

class Comments(models.Model):
    
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True,
    )

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True,
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    content = models.CharField(max_length=2000,blank=False,null=False,default=" ")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, hotel__isnull=True)
                    | models.Q(user__isnull=True, hotel__isnull=False)
                ),
                name='comment_author_is_exactly_one_of_user_or_hotel',
            )
        ]

    @property
    def author(self):
        return self.user or self.hotel


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