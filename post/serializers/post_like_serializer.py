from rest_framework import serializers


from ..models import Like


class PostLikeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Like
        fields = [
            "user",
            "post"
        ]




