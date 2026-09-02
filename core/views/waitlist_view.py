from rest_framework.views import APIView
from rest_framework import status

from core.models import Waitlister
from core.serializer.waitlister_serializer import WaitlisterSerializer
from core.utils.api_response import success_response, error_response


class WaitlistView(APIView):
    # No auth: this is the public landing-page signup.
    permission_classes = []

    def post(self, request):
        try:
            email = (request.data.get("email") or "").strip()
            existing = Waitlister.objects.filter(email__iexact=email).first()
            if existing:
                return success_response(
                    message="You're already on the waitlist",
                    data=WaitlisterSerializer(existing).data,
                    code=status.HTTP_200_OK,
                )

            serializer = WaitlisterSerializer(data=request.data)
            if not serializer.is_valid():
                return error_response(
                    message="Validation error",
                    errors=serializer.errors,
                    code=status.HTTP_400_BAD_REQUEST,
                )

            waitlister = serializer.save()
            return success_response(
                message="You're on the waitlist!",
                data=WaitlisterSerializer(waitlister).data,
                code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return error_response(
                message="An error occurred",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
