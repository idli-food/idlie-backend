from rest_framework.views import APIView
from rest_framework.response import Response
from ..services.explore_services import get_explore_page_content
from ..serializer.explore_serializer import ExplorePageSerializer
from rest_framework import status
from rest_framework.permissions import IsAuthenticated






class ExplorePageView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):
        lat = request.GET.get("lat")
        lon = request.GET.get("lon")

        if lat is None or lon is None:
            return Response(
                {"error": "lat and lon are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        radius = float(request.GET.get("radius", 10))

        posts = get_explore_page_content(
            float(lat),
            float(lon),
            radius
        )

        serializer = ExplorePageSerializer(posts)

        return Response(serializer.data)


        
