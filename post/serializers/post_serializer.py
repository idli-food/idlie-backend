from rest_framework_gis.fields import GeometryField
from rest_framework import serializers
from ..models import Post
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


    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
