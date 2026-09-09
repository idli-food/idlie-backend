from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import success_response, error_response
from post.models import Post

from ..serializers.archive_serializer import ArchivedInstantSerializer


class ArchivedInstantsView(APIView):
    """The pick list when creating an archive: the caller's own archived instants."""

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            posts = (
                Post.objects.instant()
                .filter(user_id=request.user.id, status=Post.Status.ARCHIVED)
                .prefetch_related("media")
            )
            serializer = ArchivedInstantSerializer(posts, many=True)

            return success_response(
                message="archived instants",
                data=serializer.data,
            )

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
