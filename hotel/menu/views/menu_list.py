from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from hotel.models import Menu
from hotel.menu.serializer.menu_serializer import MenuListSerializer
from core.utils.api_response import success_response, error_response


class MenuListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            menus = (
                Menu.objects.filter(hotel=request.user)
                .prefetch_related("categories__items")
            )
            return success_response(
                message="Menus fetched successfully",
                data=MenuListSerializer(menus, many=True).data,
            )
        except Exception as e:
            return error_response(
                message="An error occurred",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
