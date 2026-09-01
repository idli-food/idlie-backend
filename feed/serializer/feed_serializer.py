from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from post.models import Post
from ..services.fetch_media import get_pre_signed_url
from ..services.feed_services import get_hotel_location_link
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
    location = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    my_rating = serializers.SerializerMethodField()
    hotel_name = serializers.SerializerMethodField()

    def get_hotel_name(self, obj):
        if obj.hotel_id:
            return obj.hotel.name
        return None

    def get_location(self, obj):
        if self.context.get('platform') == 'web':
            return get_hotel_location_link(obj.hotel_id)
        if obj.location:
            return GeometryField().to_representation(obj.location)
        return None
    is_saved = serializers.SerializerMethodField()

    def get_user(self, obj):
        if obj.user_id:
            return FeedUserSerializer(obj.user).data
        if obj.hotel_id:
            return {"id": obj.hotel_id, "username": obj.hotel.name}
        return None

    def get_avatar(self, obj):
        if obj.user_id and hasattr(obj.user, "profile"):
            return FeedUserProfileSerilizer(obj.user.profile).data.get("avatar")
        if obj.hotel_id:
            return None
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

    def get_my_rating(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            rating = obj.rating.filter(user=request.user).first()
            return rating.stars if rating else None
        return None

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
            "my_rating",
            "created_at",
            "location",
            "hotel_name",
        ]
