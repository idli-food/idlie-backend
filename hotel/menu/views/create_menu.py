from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import Hotel
from hotel.menu.serializer.menu_serializer import MainMenuSerializer
from core.utils.api_response import success_response, error_response


class CreateMenuView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            hotel = Hotel.objects.get(id=request.user.id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = MainMenuSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            menu = serializer.save(hotel=hotel)
            return success_response(
                message="Menu created successfully",
                data=MainMenuSerializer(menu).data,
                code=status.HTTP_201_CREATED
            )

        except ValidationError as e:
            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message="An error occurred",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
