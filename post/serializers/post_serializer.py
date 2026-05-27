from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from ..models import Post
from ..models import Like, Comments, Saved

class CreatePostSerializer(serializers.ModelSerializer):

    location = GeometryField(required=False)

    class Meta:
        model = Post
        fields = [
            "user",
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
            "media_url",
            "like_count",
            "avg_rating",
            "rating_count",
            "composite_score",
        ]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
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
            "post",
            "content"
        ]


class PostSaveSerializer(serializers.ModelSerializer):

    class Meta:
        model = Saved
        fields = [
            "user",
            "post"
        ]