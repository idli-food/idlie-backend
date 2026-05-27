from rest_framework import serializers
from post.models import Post
from ..services.fetch_media import get_pre_signed_url
from user.models import User,UserProfile

class FeedUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
        ]
class FeedUserProfileSerilizer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            "avatar"
        ]

class FeedPostSerializer(serializers.ModelSerializer):
    user = FeedUserSerializer(read_only=True)
    avatar = FeedUserProfileSerilizer(source='user.profile', read_only=True)
    class Meta:
        model = Post
        fields = [
            "id",
            "title",
            "user",
            "avatar",
            "description",
            "media_url",
            "thumbnail_url",
            "comment_count",
            "like_count",
            "rating_count",
            "avg_rating",
            "media_type",
            "composite_score",
            "created_at",
        ]