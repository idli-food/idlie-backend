from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.post_serializer import PostRatingSerializer
from core.utils.api_response import success_response, error_response
from ..services import post_service
from ..models import Ratings
from user.models import User


class RatePostView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):

        try:

            if not isinstance(request.user, User):
                return error_response(
                    message="Only users can rate posts",
                    code=status.HTTP_403_FORBIDDEN
                )

            if post_service.check_post_availablity(post_id):
                raise ValidationError("Post not available")

            serializer = PostRatingSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            Ratings.objects.create(
                user=request.user,
                post_id=post_id,
                stars=serializer.validated_data["stars"]
            )
            post_service.update_post_rating_stats(post_id=post_id)
            return success_response(
                message="Rating saved successfully",
                code=status.HTTP_201_CREATED
            )

        except IntegrityError:

            return error_response(
                message="You have already rated this post",
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

            deleted = post_service.delete_post_rating(post_id=post_id, user_id=request.user.id)

            if not deleted:
                return error_response(
                    message="You have not rated this post",
                    code=status.HTTP_400_BAD_REQUEST
                )

            post_service.update_post_rating_stats(post_id=post_id)
            return success_response(
                message="Rating removed successfully",
                code=status.HTTP_200_OK
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
