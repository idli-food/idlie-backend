import logging
from urllib.parse import urlparse

from django.conf import settings
from django.db import transaction
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import error_response, success_response
from otp.exceptions import OTPError
from otp.tokens import consume_verification_token
from post.models import Comments, Like, PostMedia, PostRating
from post.services import post_service
from user.models import User, UserProfile

from ..jwt.cookies import clear_auth_cookies

logger = logging.getLogger(__name__)


def _delete_s3_keys(keys):
    for i in range(0, len(keys), 1000):
        chunk = keys[i:i + 1000]
        try:
            post_service.s3_client.delete_objects(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Delete={"Objects": [{"Key": key} for key in chunk]},
            )
        except Exception:
            logger.exception("failed to delete s3 objects on account deletion")


class DeleteAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        if not isinstance(user, User):
            return error_response(message="Only users can delete their account", code=403)

        verification_token = request.data.get("verification_token")
        if not verification_token:
            return error_response(message="verification_token is required")

        try:
            consume_verification_token(verification_token, expected_purpose="user_delete_account", expected_phone=user.phone)
        except OTPError as exc:
            return error_response(message=exc.message, code=exc.code)

        s3_keys = []
        for media in PostMedia.objects.filter(post__user=user):
            s3_keys.append(media.media_key)
            s3_keys.append(f"thumbnails/{media.id}.jpg")
        avatar = UserProfile.objects.filter(user=user).values_list("avatar", flat=True).first()
        if avatar:
            s3_keys.append(urlparse(avatar).path.lstrip("/") if avatar.startswith("http") else avatar)

        with transaction.atomic():
            affected_post_ids = set()
            for model in (Like, PostRating, Comments):
                affected_post_ids.update(
                    model.objects.filter(user=user).exclude(post__user=user).values_list("post_id", flat=True)
                )

            user.delete()

            for post_id in affected_post_ids:
                post_service.update_post_like_count(post_id)
                post_service.update_post_rating_stats(post_id)
                post_service.update_post_comment_count(post_id)

            transaction.on_commit(lambda: _delete_s3_keys(s3_keys))

        response = success_response(message="Account deleted")
        clear_auth_cookies(response)
        return response
