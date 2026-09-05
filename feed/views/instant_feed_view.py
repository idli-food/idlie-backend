from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import LimitOffsetPagination
from ..services.feed_services import get_instant_feed
from ..serializer.feed_serializer import FeedPostSerializer


class InstantFeedPagination(LimitOffsetPagination):
    default_limit = 20
    max_limit = 100


class InstantFeedView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = get_instant_feed()

        paginator = InstantFeedPagination()
        page = paginator.paginate_queryset(posts, request, view=self)

        platform = request.GET.get("platform")
        serializer = FeedPostSerializer(
            page, many=True, context={"request": request, "platform": platform}
        )

        return paginator.get_paginated_response(serializer.data)
