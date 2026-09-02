from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.utils.api_response import success_response, error_response
from ..services import post_service
from ..models import Post


class RatePostView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):

        try:

            if not Post.objects.filter(id=post_id, user=request.user).exists():
                return error_response(
                    message="You can only delete ratings on your own post",
                    code=status.HTTP_403_FORBIDDEN
                )

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
