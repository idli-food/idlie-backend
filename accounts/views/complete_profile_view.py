from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import ValidationError
from accounts.serializers.profile_serializer import CompleteProfileSerializer
from core.utils.api_response import success_response, error_response


class CompleteProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        try:
            profile = request.user.profile
            serializer = CompleteProfileSerializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return success_response(
                message="Profile updated",
                data={
                    "completion_percentage": profile.completion_percentage,
                    "incomplete_fields": profile.incomplete_fields,
                    "is_profile_complete": profile.is_profile_complete,
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
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
