from rest_framework import serializers
from hotel.models import HotelRating, HotelReview


class HotelRatingSerializer(serializers.ModelSerializer):
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
