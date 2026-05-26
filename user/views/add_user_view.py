# views/add_user.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError   

from ..serivices.add_user import create_user
from ..serivices.user_profile import create_user_profile
from ..serializers.user import UserResponseSerializer
from authentication.jwt.jwt_utils import create_access_token, create_refresh_token


class AddUserView(APIView):

    def post(self, request):

        try:
            user = create_user(request.data)
            response_serializer = UserResponseSerializer(user)
            create_user_profile(user)

            access_token = create_access_token(response_serializer.data["id"])
            refresh_token = create_refresh_token(response_serializer.data["id"])
            return Response(
                {
                    "status": "success",
                    "message": "User created successfully",
                    "data": response_serializer.data,
                    "access" : access_token,
                    "refresh" : refresh_token,
                },
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {   
                    "status": "failed",
                    "errors": e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    "status": "failed",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )