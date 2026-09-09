from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import success_response, error_response

from ..models import Archive
from ..serializers.archive_serializer import ArchiveSummarySerializer


class UserArchivesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):

        try:
            archives = Archive.objects.filter(user_id=user_id)
            serializer = ArchiveSummarySerializer(archives, many=True)

            return success_response(message="user archives", data=serializer.data)

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
