from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import FoodItem
from hotel.menu.serializer.menu_serializer import FoodItemSerializer
from core.utils.api_response import success_response, error_response


class FoodItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            food_item = FoodItem.objects.get(id=pk, category__menu__hotel=request.user)
        except FoodItem.DoesNotExist:
            return error_response(
                message="Food item not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = FoodItemSerializer(food_item, data=request.data, partial=True)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            serializer.save()
            return success_response(
                message="Food item updated successfully",
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
            food_item = FoodItem.objects.get(id=pk, category__menu__hotel=request.user)
        except FoodItem.DoesNotExist:
            return error_response(
                message="Food item not found",
                code=status.HTTP_404_NOT_FOUND
            )

        food_item.delete()
        return success_response(
            message="Food item deleted successfully",
            code=status.HTTP_200_OK
        )
