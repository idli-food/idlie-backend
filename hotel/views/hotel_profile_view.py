from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import Hotel
from ..serializers.hotel_serializer import HotelProfileSerializer
from ..services.hotel_services import calculate_profile_completion
from core.utils.api_response import success_response, error_response
from rest_framework.permissions import IsAuthenticated


class GetHotelProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            hotel = Hotel.objects.get(id=request.user.id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        serializer = HotelProfileSerializer(hotel)
        data = serializer.data
        data["profile_completion"] = calculate_profile_completion(hotel)

        return success_response(
            message="Hotel profile fetched successfully",
            data=data
        )

    def patch(self, request):
        try:
            hotel = Hotel.objects.get(id=request.user.id)
        except Hotel.DoesNotExist:
            return error_response(
                message="Hotel not found",
                code=status.HTTP_404_NOT_FOUND
            )

        serializer = HotelProfileSerializer(hotel, data=request.data, partial=True)
        if not serializer.is_valid():
            return error_response(
                message="Validation error",
                errors=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST
            )

        serializer.save()
        return success_response(
            message="Hotel profile updated successfully",
            data=serializer.data
        )







class UploadProfilePictureURLView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request,key):
        try :
            key = request.data.get("key")
            return success_response(
                message="Profile picture upload URL generated",
                data=result,
                code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(
                message="Failed to generate upload URL",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )