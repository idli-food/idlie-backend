from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from ..models import Tag
from core.utils.api_response import success_response


class TagListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        tags = Tag.objects.order_by("name").values("id", "name")
        return success_response(message="tags", data=list(tags))
