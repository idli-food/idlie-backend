from rest_framework import serializers
from hotel.models import HotelRating, HotelReview


class RatingUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        if hasattr(obj, "profile"):
            return obj.profile.avatar
        return None


class HotelRatingSerializer(serializers.ModelSerializer):
    user = RatingUserSerializer(read_only=True)

    class Meta:
        model = HotelRating
        fields = [
            "id",
            "user",
            "hotel",
            "rating_count",
            "created_at",
        ]
        read_only_fields = ["id", "user", "hotel", "created_at"]


class HotelReviewSerializer(serializers.ModelSerializer):
    user = RatingUserSerializer(read_only=True)

    class Meta:
        model = HotelReview
        fields = [
            "id",
            "user",
            "hotel",
            "review_text",
            "created_at",
        ]
        read_only_fields = ["id", "user", "hotel", "created_at"]
