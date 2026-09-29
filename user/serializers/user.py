


from rest_framework import serializers
from ..models import User,UserProfile

class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "phone",
            "username",
            "created_at",
        ]

        read_only_fields = fields

class UserDetailViewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['username','name','avatar','bio','dob','diet','food_preference','location']
