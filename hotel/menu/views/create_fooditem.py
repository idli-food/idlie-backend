from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import MenuCategory, FoodItem
from hotel.menu.serializer.menu_serializer import FoodItemSerializer
from core.utils.api_response import success_response, error_response


class CreateFoodItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, category_id):
        try:
            category = MenuCategory.objects.get(id=category_id, menu__hotel=request.user)
        except MenuCategory.DoesNotExist:
            return error_response(
                message="Menu category not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = FoodItemSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            food_item = serializer.save(category=category)
            return success_response(
                message="Food item created successfully",
                data=FoodItemSerializer(food_item).data,
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
