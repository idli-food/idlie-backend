from django.db.models import F
from ..models import Post, Like
from django.conf import settings


def get_s3_public_url(s3_key):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    region = settings.AWS_S3_REGION_NAME
    return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"


def check_post_availablity(post_id):
    return not Post.objects.filter(id=post_id, status=Post.Status.PUBLISHED).exists()


def update_post_like_count(post_id):
    total_like_count = Like.objects.filter(post_id=post_id).count()
    Post.objects.filter(id=post_id).update(like_count=total_like_count)


def set_media_url(post):
    try:
        if not post.raw_s3_key:
            return None

        url = get_s3_public_url(post.raw_s3_key)
        Post.objects.filter(id=post.id).update(media_url=url)

    except Post.DoesNotExist:
        return None


def set_thumbnail_url(post):
    try:
        if not post.raw_s3_key:
            return None

        url = "https://picsum.photos/200/300"
        Post.objects.filter(id=post.id).update(thumbnail_url=url)

    except Post.DoesNotExist:
        return None
