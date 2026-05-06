import boto3
import uuid

from botocore.client import Config
from django.conf import settings
from rest_framework.exceptions import ValidationError


def get_upload_url(file_name, content_type):

    if file_name is None or content_type is None:
        raise ValidationError({
            "message": "file_name or content_type is missing"
        })

    extension = file_name.split(".")[-1]

    key = f"uploads/{uuid.uuid4()}.{extension}"

    s3_client = boto3.client(
        "s3",
        region_name="ap-south-1",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
    )

    upload_url = s3_client.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": settings.AWS_STORAGE_BUCKET_NAME,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=600,
    )

    return {
        "upload_url": upload_url,
        "key": key
    }