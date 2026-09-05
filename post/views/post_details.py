from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..models import Post
from ..serializers.post_serializer import CreatePostSerializer, PostUpdateSerializer
from core.utils.api_response import success_response, error_response


class PostDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):

        try:

            try:
                post = Post.objects.get(id=post_id)
            except Post.DoesNotExist:
                return error_response(
                    message="Post not found",
                    code=status.HTTP_404_NOT_FOUND
                )

            serializer = CreatePostSerializer(post, context={"request": request})

            return success_response(
                message="post detail",
                data=serializer.data
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def patch(self, request, post_id):

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

            serializer = PostUpdateSerializer(post, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return success_response(
                message="Post updated successfully",
                data=serializer.data
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

            post.delete()

            return success_response(
                message="Post deleted successfully",
                code=status.HTTP_200_OK
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
