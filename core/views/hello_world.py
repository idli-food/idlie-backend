from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.utils.timezone import now

class HomeView(APIView):
    def get(self, request):
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Request successful",
                "data": {
                    "message": "All good and working"
                },
                "errors": None,
                "meta": {
                    "timestamp": now(),
                    "version": "1.0.0"
                }
            },
            status=status.HTTP_200_OK
        )
