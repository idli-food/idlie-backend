from django.shortcuts import get_object_or_404
from django.db.models import Max
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from core.utils.api_response import success_response, error_response

from ..models import Archive, ArchiveItem
from ..serializers.archive_serializer import (
    validate_archivable_posts,
    ArchiveDetailSerializer,
)


class ArchiveItemsView(APIView):

    permission_classes = [IsAuthenticated]

    def _get_owned_archive(self, request, archive_id):
        archive = get_object_or_404(Archive, id=archive_id)
        if archive.user_id != request.user.id:
            return None, error_response(
                message="You do not own this archive",
                code=status.HTTP_403_FORBIDDEN,
            )
        return archive, None

    def post(self, request, archive_id):

        archive, err = self._get_owned_archive(request, archive_id)
        if err:
            return err

        post_ids = list(dict.fromkeys(request.data.get("post_ids", [])))
        if not post_ids:
            return error_response(message="post_ids is required")

        try:
            posts = validate_archivable_posts(post_ids, request.user)
        except Exception as e:
            return error_response(message="Invalid posts", errors=str(e))

        existing = set(
            archive.items.filter(post_id__in=post_ids).values_list("post_id", flat=True)
        )
        start = (archive.items.aggregate(m=Max("position"))["m"] or -1) + 1

        ArchiveItem.objects.bulk_create(
            [
                ArchiveItem(archive=archive, post=post, position=start + offset)
                for offset, post in enumerate(
                    p for p in posts if p.id not in existing
                )
            ]
        )

        return success_response(
            message="items added",
            data=ArchiveDetailSerializer(archive).data,
        )

    def delete(self, request, archive_id):

        archive, err = self._get_owned_archive(request, archive_id)
        if err:
            return err

        post_ids = request.data.get("post_ids", [])
        if not post_ids:
            return error_response(message="post_ids is required")

        archive.items.filter(post_id__in=post_ids).delete()

        return success_response(
            message="items removed",
            data=ArchiveDetailSerializer(archive).data,
        )
