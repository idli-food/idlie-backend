from rest_framework import status
from rest_framework.views import APIView

from core.utils.api_response import success_response, error_response


class MeView(APIView):

    def get(self, request):
        user = request.user
        if not user or not user.is_authenticated:
            return error_response(message="Not authenticated", code=status.HTTP_401_UNAUTHORIZED)

        return success_response(
            data={
                "id": user.id,
                "username": user.username,
                "phone_number": user.phone,
            }
        )
