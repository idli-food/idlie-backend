from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from post.services.signed_url import get_upload_url
from core.utils.api_response import success_response, error_response


class AvatarUploadUrlView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            file_name = request.data.get("file_name")
            content_type = request.data.get("content_type")
            result = get_upload_url(file_name, content_type)
            return success_response(
                message="Avatar upload URL generated",
                data=result,
                code=status.HTTP_200_OK
            )
        except Exception as e:
            return error_response(
                message="Failed to generate upload URL",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
