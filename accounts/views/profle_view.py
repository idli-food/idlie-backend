from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from ..serializers.profile_serializer import ProfileViewSerializer


class ProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self,request):

        serializer = ProfileViewSerializer(request.user.profile)

        return Response(serializer.data)


        


