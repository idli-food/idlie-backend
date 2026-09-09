from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import success_response, error_response

from ..models import Archive
from ..serializers.archive_serializer import (
    ArchiveSummarySerializer,
    ArchiveDetailSerializer,
    ArchiveWriteSerializer,
)


class ArchiveListCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        try:
            archives = Archive.objects.filter(user_id=request.user.id)
            serializer = ArchiveSummarySerializer(archives, many=True)

            return success_response(message="archives", data=serializer.data)

        except Exception as e:

            return error_response(
                message="Something went wrong",
                errors=str(e),
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):

        serializer = ArchiveWriteSerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return error_response(
                message="Invalid data",
                errors=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST,
            )

        archive = serializer.save()
        return success_response(
            message="archive created",
            data=ArchiveDetailSerializer(archive).data,
            code=status.HTTP_201_CREATED,
        )


class ArchiveDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, archive_id):

        archive = get_object_or_404(Archive, id=archive_id)
        return success_response(
            message="archive",
            data=ArchiveDetailSerializer(archive).data,
        )

    def patch(self, request, archive_id):

        archive = get_object_or_404(Archive, id=archive_id)
        if archive.user_id != request.user.id:
            return error_response(
                message="You do not own this archive",
                code=status.HTTP_403_FORBIDDEN,
            )

        serializer = ArchiveWriteSerializer(
            archive, data=request.data, partial=True, context={"request": request}
        )
        if not serializer.is_valid():
            return error_response(
                message="Invalid data",
                errors=serializer.errors,
                code=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()
        return success_response(
            message="archive updated",
            data=ArchiveDetailSerializer(archive).data,
        )

    def delete(self, request, archive_id):

        archive = get_object_or_404(Archive, id=archive_id)
        if archive.user_id != request.user.id:
            return error_response(
                message="You do not own this archive",
                code=status.HTTP_403_FORBIDDEN,
            )

        archive.delete()
        return success_response(message="archive deleted")
