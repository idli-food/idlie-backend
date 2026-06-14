from rest_framework import serializers
from django.contrib.gis.geos import Point
from user.models import User, UserProfile
from post.serializers.post_serializer import PostProfilePageSerializer


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


class CompleteProfileSerializer(serializers.ModelSerializer):
    lat = serializers.FloatField(write_only=True, required=False)
    lon = serializers.FloatField(write_only=True, required=False)

    class Meta:
        model = UserProfile
        fields = ['name', 'bio', 'dob', 'diet', 'food_preference', 'avatar', 'lat', 'lon']
        extra_kwargs = {
            'name': {'required': False},
            'bio': {'required': False, 'allow_blank': True},
            'dob': {'required': False},
            'diet': {'required': False, 'allow_blank': True},
            'food_preference': {'required': False, 'allow_blank': True},
            'avatar': {'required': False},
        }

    def validate(self, data):
        lat = data.get('lat')
        lon = data.get('lon')
        if (lat is None) != (lon is None):
            raise serializers.ValidationError("Both lat and lon are required together.")
        return data

    def update(self, instance, validated_data):
        lat = validated_data.pop('lat', None)
        lon = validated_data.pop('lon', None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if lat is not None and lon is not None:
            instance.location = Point(lon, lat, srid=4326)

        instance.save()
        return instance