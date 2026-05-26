from rest_framework import serializers
from post.models import Post
from ..services.fetch_media import get_pre_signed_url
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
    media_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
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
            "media_type",
            "composite_score",
            "created_at",
        ]
    
    def get_media_url(self,obj):

        if not obj.raw_s3_key:
            return None
        
        
        url = get_pre_signed_url(obj.raw_s3_key)

        if not url: 
            return None
        return url
    def get_thumbnail_url(self,obj):

        url = None
        return None