from datetime import timedelta

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..models import Post
from ..serializers.post_serializer import CreatePostSerializer
from core.utils.api_response import success_response, error_response


class RepostView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:

            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return error_response(
                    message="Post not found",
                    code=status.HTTP_404_NOT_FOUND
                )

            if post.user_id != request.user.id and post.hotel_id != request.user.id:
                return error_response(
                    message="You do not own this post",
                    code=status.HTTP_403_FORBIDDEN
                )

            if post.post_type != Post.PostType.INSTANT:
                return error_response(
                    message="Only instant posts can be reposted",
                    code=status.HTTP_400_BAD_REQUEST
                )

            if post.status != Post.Status.ARCHIVED:
                return error_response(
                    message="Only archived posts can be reposted",
                    code=status.HTTP_400_BAD_REQUEST
                )

            post.status = Post.Status.PUBLISHED
            post.expires_at = timezone.now() + timedelta(hours=24)
            post.archived_at = None
            post.save(update_fields=["status", "expires_at", "archived_at"])

            return success_response(
                message="Post reposted successfully",
                data=CreatePostSerializer(post, context={"request": request}).data
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
