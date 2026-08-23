from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import Menu, MenuCategory
from hotel.menu.serializer.menu_serializer import MenuCategorySerializer
from core.utils.api_response import success_response, error_response


class CreateMenuCategoryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id, hotel=request.user)
        except Menu.DoesNotExist:
            return error_response(
                message="Menu not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = MenuCategorySerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            category = serializer.save(menu=menu)
            return success_response(
                message="Menu category created successfully",
                data=MenuCategorySerializer(category).data,
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
