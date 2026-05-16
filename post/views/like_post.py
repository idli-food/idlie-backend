from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..serializers.post_like_serializer import PostLikeSerializer
from ..utils.api_response import success_response, error_response
from ..services.post_validation import PostValidations


class LikePostView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:

            if PostValidations.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            serializer = PostLikeSerializer(data={
                "user": request.user.id,
                "post": post_id
            })

            serializer.is_valid(raise_exception=True)

            serializer.save()

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