from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user.models import UserProfile
from ..serializers.profile_serializer import ProfileViewSerializer


class UserProfileView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response(
                {"detail": "Profile not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        except Exception as e:
            return Response(
                {"detail": "Failed to retrieve profile.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = ProfileViewSerializer(profile)
        return Response(serializer.data)
