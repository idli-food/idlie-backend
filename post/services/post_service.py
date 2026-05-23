from django.db.models import F
from ..models import Post,Like
import boto3
from django.conf import settings



def get_pre_signed_url(s3_key,expiry_seconds=3600):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    url = s3_client.generate_presigned_url(
        ClientMethod="get_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": s3_key,
        },
        ExpiresIn=expiry_seconds,
    )

    return url


def check_post_availablity(post_id):
    return not Post.objects.filter(id=post_id,status=Post.Status.PUBLISHED).exists()
    

def update_post_like_count(post_id):
    total_like_count = Like.objects.filter(post_id=post_id).count()
    Post.objects.filter(id=post_id).update(like_count=total_like_count)



def set_media_url(post):
    print(post.raw_s3_key)

    try:

        if not post.raw_s3_key:
            return None

        url = get_pre_signed_url(post.raw_s3_key)
        print(url)
        p = Post.objects.filter(id=post.id).update(media_url = url)
        print("-------------------")

    except Post.DoesNotExist:
        return None

def set_thumbnail_url(post):

    try:

        if not post.raw_s3_key:
            return None

        url = "https://picsum.photos/200/300"

        Post.objects.filter(id=post.id).update(thumbnail_url = url)
        print("++++++++++++++")

    except Post.DoesNotExist:
        return None
