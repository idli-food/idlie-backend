from rest_framework import serializers
from user.models import User,UserProfile
from  post.serializers.post_serializer import PostProfilePageSerializer


class ProfileViewSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    total_post = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_stars = serializers.SerializerMethodField()
    total_rating = serializers.SerializerMethodField()
    total_post = serializers.SerializerMethodField()
    posts = serializers.SerializerMethodField()
    completion_percentage = serializers.ReadOnlyField()
    incomplete_fields = serializers.ReadOnlyField()
    is_profile_complete = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            "username",
            "name",
            "avatar",
            "bio",
            "total_post",
            "total_likes",
            "total_stars",
            "total_rating",
            "total_post",
            "posts",
            "is_verified",
            'completion_percentage', 'incomplete_fields', 'is_profile_complete',
            
        ]
        read_only_fields = fields

    def get_total_stars(self, obj):
        return 10000

    def get_total_rating(self, obj):
        return obj.user.rating.count()

    def get_total_likes(self, obj):
        return obj.user.likes.count()

    def get_total_post(self, obj):
        return obj.user.posts.count()
    def get_posts(self, obj):
        posts = obj.user.posts.all()
        return PostProfilePageSerializer(posts, many=True).data