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
    user = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    def get_user(self, obj):
        if obj.hotel_id:
            return {"id": obj.hotel_id, "username": obj.hotel.name}
        if obj.user_id:
            return FeedUserSerializer(obj.user).data
        return None

    def get_avatar(self, obj):
        if obj.hotel_id:
            return None
        if obj.user_id and hasattr(obj.user, "profile"):
            return FeedUserProfileSerilizer(obj.user.profile).data.get("avatar")
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_is_saved(self,obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.saved.filter(user = request.user).exists()

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
            "is_liked",
            "is_saved",
            "created_at",
            "location"
        ]
    def get_location(self,obj):
        if not obj:
            return None
        
        point = str(obj.location)
        coords = point.replace("SRID=4326;POINT (", "").replace(")", "")
        longitude, latitude = map(float,coords.split())
        return {
            "latitude" : latitude,
            "longitude" : longitude
        }
    