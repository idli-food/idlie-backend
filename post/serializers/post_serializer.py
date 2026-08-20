from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from ..models import Post
from ..models import Like, Comments, Saved
from user.serivices.user_service import get_avatar_url
from hotel.models import Hotel

class   CreatePostSerializer(serializers.ModelSerializer):

    location = GeometryField(required=False)

    class Meta:
        model = Post
        fields = [
            "user",
            "hotel",
            "food_spot",
            "title",
            "description",
            "media_type",
            "raw_s3_key",
            "media_url",
            "thumbnail_url",
            "status",
            "like_count",
            "avg_rating",
            "rating_count",
            "composite_score",
            "location",
        ]

        read_only_fields = [
            "user",
            "hotel",
            "media_url",
            "like_count",
            "avg_rating",
            "rating_count",
            "composite_score",
        ]

    def create(self, validated_data):
        principal = self.context["request"].user
        if isinstance(principal, Hotel):
            validated_data["hotel"] = principal
        else:
            validated_data["user"] = principal
        return super().create(validated_data)




class PostProfilePageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            "thumbnail_url"
        ]

class PostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = [
            "user",
            "post"
        ]
class PostCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comments
        fields = [
            "user",
            "hotel",
            "post",
            "content"
        ]
        extra_kwargs = {
            "user": {"required": False},
            "hotel": {"required": False},
        }

class PostSaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Saved
        fields = [
            "user",
            "post"
        ]

class FeedPostCommentSerializer(serializers.ModelSerializer):

    username = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = Comments
        fields = [
            "id",
            "username",
            "content",
            "avatar",
            "created_at"
        ]

    def get_username(self, obj):
        if obj.hotel_id:
            return obj.hotel.name
        return obj.user.username

    def get_avatar(self, obj):
        if obj.hotel_id:
            return None
        return get_avatar_url(obj.user.id)


class SavedPostSerilizer(serializers.ModelSerializer):


    class Meta:
        model = Post
        fields = [
            "id",
            "thumbnail_url",
            "media_type",
        ]

class SavedPostFeedSerilizer(serializers.ModelSerializer):


    class Meta:
        model = Post
        fields = [
            "id",
            "thumbnail_url",
            "media_type",
        ]