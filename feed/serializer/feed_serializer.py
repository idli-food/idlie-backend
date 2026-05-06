from rest_framework import serializers
from post.models import Post

from user.models import User

class FeedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "avatar_url",
        ]

class FeedPostSerializer(serializers.ModelSerializer):
    user = FeedUserSerializer(read_only=True)
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "user",
            "description",
            "media_url",
            "thumbnail_url",
            "like_count",
            "avg_rating",
            "composite_score",
            "created_at",
        ]

