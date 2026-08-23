from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import FoodItem, FoodItemVariant
from hotel.menu.serializer.menu_serializer import FoodItemVariantSerializer
from core.utils.api_response import success_response, error_response


class CreateFoodItemVariantView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, food_item_id):
        try:
            food_item = FoodItem.objects.get(id=food_item_id, category__menu__hotel=request.user)
        except FoodItem.DoesNotExist:
            return error_response(
                message="Food item not found",
                code=status.HTTP_404_NOT_FOUND
            )

        try:
            serializer = FoodItemVariantSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST
                )

            variant = serializer.save(food_item=food_item)
            return success_response(
                message="Food item variant created successfully",
                data=FoodItemVariantSerializer(variant).data,
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
