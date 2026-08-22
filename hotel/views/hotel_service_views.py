from rest_framework import status
from rest_framework.views import APIView
from ..models import Hotel
from ..serializers.hotel_serializer import HotelProfileSerializer
from ..services.hotel_services import calculate_profile_completion
from core.utils.api_response import success_response, error_response
from rest_framework.permissions import IsAuthenticated
from user.serivices.user_service import get_avatar_upload_url










class UploadProfilePictureURLView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try :
            file_name = request.data.get("file_name")
            content_type = request.data.get("content_type")
            result = get_avatar_upload_url(file_name, content_type, role="hotel")
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