from rest_framework import serializers
from user.models import User


class ProfileViewSerializer(serializers.ModelSerializer):

    total_post = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_stars = serializers.SerializerMethodField()
    total_rating = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "phone",
            "username",
            "first_name",
            "last_name",
            "avatar_url",
            "bio",
            "total_post",
            "total_likes",
            "total_stars",
            "total_rating",
            "is_verified",
        ]
        read_only_fields = fields

    def get_total_stars(self, obj):
        return 10000

    def get_total_rating(self, obj):
        return obj.rating.count()

    def get_total_likes(self, obj):
        return obj.likes.count()

    def get_total_post(self, obj):
        return obj.posts.count()