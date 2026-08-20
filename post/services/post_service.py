from django.db.models import F
from ..models import Post, Like, Comments, Saved
from django.conf import settings
from hotel.models import Hotel
import boto3


s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)

def get_s3_public_url(s3_key):
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    region = settings.AWS_S3_REGION_NAME
    return f"https://{bucket}.s3.{region}.amazonaws.com/{s3_key}"


def check_post_availablity(post_id):
    return not Post.objects.filter(id=post_id, status=Post.Status.PUBLISHED).exists()


def update_post_like_count(post_id):
    total_like_count = Like.objects.filter(post_id=post_id).count()
    Post.objects.filter(id=post_id).update(like_count=total_like_count)


def delete_post_like(post_id, user_id):
    deleted, _ = Like.objects.filter(post_id=post_id, user_id=user_id).delete()
    return deleted > 0


def set_media_url(post):
    try:
        if not post.raw_s3_key:
            return None

        url = get_s3_public_url(post.raw_s3_key)
        Post.objects.filter(id=post.id).update(media_url=url)

    except Post.DoesNotExist:
        return None


def set_thumbnail_url_image(post_id):
    updated = Post.objects.filter(id=post_id).update(thumbnail_url=F('media_url'))
    if not updated:
        return None


def update_post_comment_count(post_id):
    total_comments = Comments.objects.filter(post_id = post_id).count()
    Post.objects.filter(id = post_id).update(comment_count = total_comments)


def delete_comment(comment_id, author):
    if isinstance(author, Hotel):
        deleted, _ = Comments.objects.filter(id=comment_id, hotel_id=author.id).delete()
    else:
        deleted, _ = Comments.objects.filter(id=comment_id, user_id=author.id).delete()
    return deleted > 0

def unsave_post(post_id, user_id):
    deleted, _ = Saved.objects.filter(post_id=post_id, user_id=user_id).delete()
    return deleted > 0

def get_comments(post_id):
    comments = Comments.objects.filter(post_id = post_id)
    return comments

 
def get_saved_post(user_id):
    return Post.objects.filter(saved__user_id=user_id)


def upload_file_to_s3(
    file_path: str,
    s3_key: str,
    content_type: str = None,
) -> str:

    extra_args = {}

    if content_type:
        extra_args["ContentType"] = content_type

    s3_client.upload_file(
        Filename=file_path,
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=s3_key,
        ExtraArgs=extra_args if extra_args else None,
    )

    return (
        f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3."
        f"{settings.AWS_S3_REGION_NAME}.amazonaws.com/{s3_key}"
    )