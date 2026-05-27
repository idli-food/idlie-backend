from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.post_like_serializer import PostLikeSerializer
from core.utils.api_response import success_response, error_response
from ..services import post_service


class LikePostView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:

            if post_service.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            serializer = PostLikeSerializer(data={
                "user": request.user.id,
                "post": post_id
            })

            serializer.is_valid(raise_exception=True)

            serializer.save()
            post_service.update_post_like_count(post_id=post_id)
            return success_response(
                message="Liked successfully",
                code=status.HTTP_201_CREATED
            )

        except IntegrityError:

            return error_response(
                message="You already liked this post",
                code=status.HTTP_400_BAD_REQUEST
            )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, post_id):

        try:

            if post_service.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            deleted = post_service.delete_post_like(post_id=post_id, user_id=request.user.id)

            if not deleted:
                return error_response(
                    message="You have not liked this post",
                    code=status.HTTP_400_BAD_REQUEST
                )

            post_service.update_post_like_count(post_id=post_id)
            return success_response(
                message="Like removed successfully",
                code=status.HTTP_200_OK
            )

        except ValidationError as e:

            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    