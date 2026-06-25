from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.profile_serializer import ProfileViewSerializer


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            serializer = ProfileViewSerializer(request.user.profile)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": "Failed to retrieve profile.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


        


