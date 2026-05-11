from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ..serializers.login_serializer import LoginSerializer
from authentication.jwt.jwt_utils import create_access_token,create_refresh_token

class LoginView(APIView):

    permission_classes = []

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]

        access_token = create_access_token(user_id=user.id)
        refresh_token = create_refresh_token(user_id=user.id)

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "phone_number": user.phone,
            },
            "tokens": {
                "access": access_token,
                "refresh": refresh_token,
            }
        }, status=status.HTTP_200_OK)