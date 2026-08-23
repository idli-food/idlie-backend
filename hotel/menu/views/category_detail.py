from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import MenuCategory
from hotel.menu.serializer.menu_serializer import MenuCategorySerializer
from core.utils.api_response import success_response, error_response


class MenuCategoryDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            category = MenuCategory.objects.get(id=pk, menu__hotel=request.user)
        except MenuCategory.DoesNotExist:
            return error_response(
                message="Menu category not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = MenuCategorySerializer(category, data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return success_response(
                message="Menu category updated successfully",
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
            category = MenuCategory.objects.get(id=pk, menu__hotel=request.user)
        except MenuCategory.DoesNotExist:
            return error_response(
                message="Menu category not found",
                code=status.HTTP_404_NOT_FOUND
            )

        category.delete()
        return success_response(
            message="Menu category deleted successfully",
            code=status.HTTP_200_OK
        )
