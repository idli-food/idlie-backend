# views/add_user.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from ..serivices.add_user import create_user
from ..serializers.user import UserResponseSerializer


class AddUserView(APIView):

    def post(self, request):

        try:
            user = create_user(request.data)
            response_serializer = UserResponseSerializer(user)
            return Response(
                {
                    "status": "success",
                    "message": "User created successfully",
                    "data": response_serializer.data
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