import os
import tempfile
import subprocess
import requests
from celery import shared_task
from django.conf import settings

from post.models import PostMedia
from .post_service import upload_file_to_s3



@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def generate_thumbnail(self, post_media_id):

    post_media = PostMedia.objects.get(id=post_media_id)

    temp_video_path = None
    temp_thumbnail_path = None

    try:

        response = requests.get(post_media.media_url, stream=True)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False
        ) as video_file:

            for chunk in response.iter_content(chunk_size=8192):
                video_file.write(chunk)

            temp_video_path = video_file.name

        # Create thumbnail file
        with tempfile.NamedTemporaryFile(
            suffix=".jpg",
            delete=False
        ) as thumbnail_file:

            temp_thumbnail_path = thumbnail_file.name

        # Generate thumbnail at 2 seconds
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                "2",
                "-i",
                temp_video_path,
                "-frames:v",
                "1",
                temp_thumbnail_path,
            ],
            check=True,
            capture_output=True,
        )

        # Upload thumbnail to S3
        thumbnail_url = upload_file_to_s3(
            file_path=temp_thumbnail_path,
            s3_key=f"thumbnails/{post_media.id}.jpg",
        )

        # Save URL
        post_media.thumbnail_url = thumbnail_url
        post_media.upload_status = PostMedia.UploadStatus.UPLOADED
        post_media.save(update_fields=["thumbnail_url", "upload_status"])
    except Exception as exc:
        post_media.upload_status = PostMedia.UploadStatus.FAILED
        post_media.save(update_fields=["upload_status"])
        raise self.retry(exc=exc)

    finally:

        if temp_video_path and os.path.exists(temp_video_path):
            os.remove(temp_video_path)

        if temp_thumbnail_path and os.path.exists(temp_thumbnail_path):
            os.remove(temp_thumbnail_path)