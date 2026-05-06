from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from rest_framework import status

from ..services.signed_url import get_upload_url
from ..utils.api_response import success_response, error_response


class GenerateUploadUrlView(APIView):

    def post(self, request):
        file_name = request.data.get("file_name")
        content_type = request.data.get("content_type")

        try:
            url = get_upload_url(file_name, content_type)

            return success_response(
                message="Upload URL generated successfully",
                data={
                    "upload_url": url["upload_url"],
                    "key": url["key"]
                }
            )

        except ValidationError as e:
            return error_response(
                message="Validation error",
                errors=e.detail,
                code=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return error_response(
                message=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )