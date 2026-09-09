from rest_framework import serializers

from post.models import Post
from post.serializers.post_serializer import PostMediaSerializer
from post.services import post_service

from ..models import Archive, ArchiveItem


def validate_archivable_posts(post_ids, user):
    """Return the user's own archived instant posts for the given ids, or raise."""

    posts = list(
        Post.objects.filter(
            id__in=post_ids,
            user_id=user.id,
            post_type=Post.PostType.INSTANT,
            status=Post.Status.ARCHIVED,
        )
    )

    found_ids = {post.id for post in posts}
    invalid = [pid for pid in post_ids if pid not in found_ids]
    if invalid:
        raise serializers.ValidationError(
            f"Posts {invalid} are not your archived instant posts."
        )

    return posts


class ArchivedInstantSerializer(serializers.ModelSerializer):

    media = PostMediaSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = ["id", "media"]


class ArchiveItemSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source="post.id", read_only=True)
    media = PostMediaSerializer(source="post.media", many=True, read_only=True)

    class Meta:
        model = ArchiveItem
        fields = ["id", "position", "media"]


class ArchiveSummarySerializer(serializers.ModelSerializer):

    item_count = serializers.SerializerMethodField()
    preview = serializers.SerializerMethodField()

    class Meta:
        model = Archive
        fields = ["id", "name", "emoji", "cover_url", "item_count", "preview"]

    def get_item_count(self, obj):
        return obj.items.count()

    def get_preview(self, obj):
        first = obj.items.first()
        if not first:
            return []
        return PostMediaSerializer(first.post.media.all(), many=True).data


class ArchiveDetailSerializer(ArchiveSummarySerializer):

    items = ArchiveItemSerializer(many=True, read_only=True)

    class Meta(ArchiveSummarySerializer.Meta):
        fields = ArchiveSummarySerializer.Meta.fields + ["items"]


class ArchiveWriteSerializer(serializers.ModelSerializer):

    post_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Archive
        fields = ["id", "name", "emoji", "cover_url", "post_ids"]

    def validate_post_ids(self, value):
        return list(dict.fromkeys(value))

    def validate(self, attrs):
        if self.instance is None and not attrs.get("post_ids"):
            raise serializers.ValidationError(
                {"post_ids": "Select at least one archived instant post."}
            )
        return attrs

    def _resolve_cover(self, cover_url):
        if cover_url and not cover_url.startswith("http"):
            return post_service.get_s3_public_url(cover_url)
        return cover_url

    def create(self, validated_data):
        post_ids = validated_data.pop("post_ids")
        user = self.context["request"].user

        posts = validate_archivable_posts(post_ids, user)

        validated_data["cover_url"] = self._resolve_cover(
            validated_data.get("cover_url", "")
        )
        archive = Archive.objects.create(user=user, **validated_data)

        ArchiveItem.objects.bulk_create(
            [
                ArchiveItem(archive=archive, post=post, position=index)
                for index, post in enumerate(posts)
            ]
        )
        return archive

    def update(self, instance, validated_data):
        validated_data.pop("post_ids", None)
        if "cover_url" in validated_data:
            validated_data["cover_url"] = self._resolve_cover(
                validated_data["cover_url"]
            )
        for field, value in validated_data.items():
            setattr(instance, field, value)
        instance.save()
        return instance

    def to_representation(self, instance):
        return ArchiveDetailSerializer(instance, context=self.context).data
