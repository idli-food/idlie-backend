from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.utils.api_response import success_response, error_response
from feed.serializer.feed_serializer import FeedPostSerializer
from post.services import post_service


class MyPostsView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            posts = post_service.get_regular_posts_by_user(request.user.id)
            serializer = FeedPostSerializer(posts, many=True, context={'request': request})

            return success_response(
                message="my posts",
                data=serializer.data
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
