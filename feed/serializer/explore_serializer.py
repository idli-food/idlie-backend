from rest_framework import serializers
from post.models import Post
from post.serializers.post_serializer import PostMediaSerializer



class ExplorePageSerializer(serializers.ModelSerializer):

    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "media"
        ]
