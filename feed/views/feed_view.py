from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.feed_services import get_feed_by_post_rating
from ..serializer.feed_serializer import FeedPostSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class FeedView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request):

        # lat = request.GET.get("lat")
        # lon = request.GET.get("lon")

        # if lat is None or lon is None:
        #     return Response(
        #         {"error": "lat and lon are required"},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        # radius = float(request.GET.get("radius", 10))

        platform = request.GET.get("platform")

        posts = get_feed_by_post_rating()

        serializer = FeedPostSerializer(posts, many=True, context={'request': request, 'platform': platform})
        print("Serialized feed data:", serializer.data)  # Debugging line

        return Response(serializer.data)