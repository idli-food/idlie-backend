from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response








class HotelTestView(APIView):

    def get(self, request):
        return Response({"message": "Hotel test view is working!"}, status=status.HTTP_200_OK)






