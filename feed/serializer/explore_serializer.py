from rest_framework import serializers
from post.models import Post



class ExplorePageSerializer(serializers.ModelSerializer):


    class Meta:
        model = Post
        fields = [
            "id",
            "thumbnail_url"
        ]
