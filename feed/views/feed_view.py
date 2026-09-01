from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.feed_services import get_feed_by_post_rating
from ..serializer.feed_serializer import FeedPostSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

class FeedView(APIView):

    permission_classes = [IsAuthenticated]


    def get(self, request):

        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        try:
            lat = float(lat) if lat is not None else None
            lon = float(lon) if lon is not None else None
        except ValueError:
            return Response(
                {"error": "Invalid lat or lon"},
                status=status.HTTP_400_BAD_REQUEST
            )

        platform = request.GET.get("platform")

        posts = get_feed_by_post_rating(lat, lon)

        serializer = FeedPostSerializer(posts, many=True, context={'request': request, 'platform': platform})
        print("Serialized feed data:", serializer.data)  # Debugging line

        return Response(serializer.data)