from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..models import User
from core.utils.api_response import success_response, error_response


class SetUserStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not isinstance(request.user, User) or not request.user.is_staff:
            return error_response(
                message="Only staff can change staff status",
                code=status.HTTP_403_FORBIDDEN
            )

        try:
            target = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return error_response(
                message="User not found",
                code=status.HTTP_404_NOT_FOUND
            )

        is_staff = request.data.get("is_staff")
        if not isinstance(is_staff, bool):
            return error_response(
                message="'is_staff' must be a boolean",
                code=status.HTTP_400_BAD_REQUEST
            )

        target.is_staff = is_staff
        target.save(update_fields=["is_staff"])

        return success_response(
            message="Staff status updated successfully",
            data={"id": target.id, "username": target.username, "is_staff": target.is_staff},
        )
