from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import Hotel, Menu
from hotel.menu.serializer.menu_serializer import MainMenuSerializer, MenuDetailSerializer
from core.utils.api_response import success_response, error_response


class MenuDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=request.user.id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            menu = (
                Menu.objects.prefetch_related("categories__items__variants")
                .get(id=pk, hotel=hotel)
            )
        except Menu.DoesNotExist:
            return error_response(
                message="Menu not found",
                code=status.HTTP_404_NOT_FOUND
            )

        serializer = MenuDetailSerializer(menu)
        return success_response(
            message="Menu retrieved successfully",
            data=serializer.data
        )

    def patch(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=request.user.id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            menu = Menu.objects.get(id=pk, hotel=hotel)
        except Menu.DoesNotExist:
            return error_response(
                message="Menu not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = MainMenuSerializer(menu, data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return success_response(
                message="Menu updated successfully",
                data=serializer.data
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

    def delete(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=request.user.id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            menu = Menu.objects.get(id=pk, hotel=hotel)
        except Menu.DoesNotExist:
            return error_response(
                message="Menu not found",
                code=status.HTTP_404_NOT_FOUND
            )

        menu.delete()
        return success_response(
            message="Menu deleted successfully",
            code=status.HTTP_200_OK
        )
