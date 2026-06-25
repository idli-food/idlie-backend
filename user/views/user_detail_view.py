
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..serializers.user import UserDetailViewSerializer


class UserDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        
        serializer = UserDetailViewSerializer(request.user.profile)

        return(Response(serializer.data))
