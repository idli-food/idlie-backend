from datetime import timedelta
from django.utils import timezone
from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from ..models import Post, PostMedia
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


class PostMediaSerializer(serializers.ModelSerializer):

    class Meta:
        model = PostMedia
        fields = [
            "content_type",
            "category",
            "position",
            "media_key",
            "media_url",
            "thumbnail_url",
        ]
        read_only_fields = [
            "media_url",
            "thumbnail_url",
        ]


class   CreatePostSerializer(serializers.ModelSerializer):

    location = GeometryField(required=False)
    ratings = PostRatingSerializer(many=True, write_only=True, required=False)
    media = PostMediaSerializer(many=True, write_only=True)

    class Meta:
        model = Post
        fields = [
            "user",
            "hotel",
            "description",
            "status",
            "post_type",
            "like_count",
            "avg_rating",
            "rating_count",
            "composite_score",
            "location",
            "ratings",
            "media",
        ]

        read_only_fields = [
            "user",
            "like_count",
            "avg_rating",
            "rating_count",
            "composite_score",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["media"] = PostMediaSerializer(instance.media.all(), many=True).data
        return data

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
        elif ratings:
            given = [r["category"] for r in ratings]
            if sorted(given) != sorted(required_categories):
                raise serializers.ValidationError(
                    {"ratings": "Provide exactly one rating for each of: "
                                f"{', '.join(sorted(required_categories))}."}
                )

        if attrs.get("post_type") == Post.PostType.INSTANT:
            media = attrs.get("media") or []
            item = media[0] if len(media) == 1 else None
            if (
                item is None
                or item.get("content_type") != PostMedia.ContentType.VIDEO
                or item.get("category") != PostMedia.Category.INSTANT
            ):
                raise serializers.ValidationError(
                    {"media": "Instant posts must be a single video with "
                              "category 'instant'."}
                )

        return attrs

    def create(self, validated_data):
        principal = self.context["request"].user
        ratings = validated_data.pop("ratings", [])
        media_items = validated_data.pop("media")

        if validated_data.get("post_type") == Post.PostType.INSTANT:
            validated_data["expires_at"] = timezone.now() + timedelta(hours=24)

        if isinstance(principal, Hotel):
            validated_data["hotel"] = principal
            post = super().create(validated_data)
            self._create_media(post, media_items)
            return post

        validated_data["user"] = principal
        post = super().create(validated_data)
        self._create_media(post, media_items)

        PostRating.objects.bulk_create([
            PostRating(user=principal, post=post, **rating)
            for rating in ratings
        ])
        post_service.update_post_rating_stats(post.id)
        return post

    def _create_media(self, post, media_items):
        PostMedia.objects.bulk_create([
            PostMedia(post=post, position=item.get("position", index), **{
                k: v for k, v in item.items() if k != "position"
            })
            for index, item in enumerate(media_items)
        ])




class PostUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = [
            "description",
        ]


class PostProfilePageSerializer(serializers.ModelSerializer):

    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "media"
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

    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "media",
        ]

class SavedPostFeedSerilizer(serializers.ModelSerializer):

    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "media",
        ]