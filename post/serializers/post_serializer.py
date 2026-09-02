from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from ..models import Post
from ..models import Like, Comments, Saved, PostRating
from ..services import post_service
from user.serivices.user_service import get_avatar_url
from hotel.models import Hotel


class PostRatingSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostRating
        fields = [
            "category",
            "score",
            "review",
        ]


class   CreatePostSerializer(serializers.ModelSerializer):

    location = GeometryField(required=False)
    ratings = PostRatingSerializer(many=True, write_only=True, required=False)

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
            "ratings",
        ]

        read_only_fields = [
            "user",
            "media_url",
            "like_count",
            "avg_rating",
            "rating_count",
            "composite_score",
        ]

    def validate(self, attrs):
        principal = self.context["request"].user
        is_hotel = isinstance(principal, Hotel)

        if not is_hotel and not attrs.get("hotel"):
            raise serializers.ValidationError({"hotel": "This field is required."})

        ratings = attrs.get("ratings")
        required_categories = set(PostRating.Category.values)

        if is_hotel:
            if ratings:
                raise serializers.ValidationError(
                    {"ratings": "Hotels cannot rate posts."}
                )
        else:
            given = [r["category"] for r in ratings or []]
            if sorted(given) != sorted(required_categories):
                raise serializers.ValidationError(
                    {"ratings": "Provide exactly one rating for each of: "
                                f"{', '.join(sorted(required_categories))}."}
                )

        return attrs

    def create(self, validated_data):
        principal = self.context["request"].user
        ratings = validated_data.pop("ratings", [])

        if isinstance(principal, Hotel):
            validated_data["hotel"] = principal
            return super().create(validated_data)

        validated_data["user"] = principal
        post = super().create(validated_data)

        PostRating.objects.bulk_create([
            PostRating(user=principal, post=post, **rating)
            for rating in ratings
        ])
        post_service.update_post_rating_stats(post.id)
        return post




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