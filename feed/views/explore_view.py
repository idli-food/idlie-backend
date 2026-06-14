from rest_framework.views import APIView
from ..services.explore_services import get_explore_page_content
from ..serializer.explore_serializer import ExplorePageSerializer
from feed.serializer.feed_serializer import FeedPostSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.utils.api_response import success_response, error_response


class ExplorePageView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        if lat is None or lon is None:
            return error_response(
                message="lat and lon are required",
                code=status.HTTP_400_BAD_REQUEST
            )

        try:
            radius = float(request.GET.get("radius", 10))
            posts = get_explore_page_content(float(lat), float(lon), radius)

            if request.query_params.get("view") == "feed":
                start_id = request.query_params.get("start_id")
                posts = list(posts)
                if start_id:
                    idx = next((i for i, p in enumerate(posts) if p.id == int(start_id)), None)
                    if idx is not None:
                        posts = posts[idx:] + posts[:idx]
                serializer = FeedPostSerializer(posts, many=True, context={'request': request})
            else:
                serializer = ExplorePageSerializer(posts, many=True)

            return success_response(
                message="explore",
                data=serializer.data
            )

        except ValueError:
            return error_response(
                message="Invalid lat, lon, or radius",
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
