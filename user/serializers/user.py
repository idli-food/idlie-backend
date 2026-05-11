


from rest_framework import serializers
from ..models import User

class AddUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)
    class Meta:
        model = User
        fields = [
            'phone',
            'username',
            'password',
        ]
    def create(self,validate_data):
        user = User.objects.create_user(
            username=validate_data['user_name'],
            phone = validate_data['phone'],
            password= validate_data['password']
        )
        return user


class UserResponseSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

        fields = [
            "id",
            "phone",
            "username",
            "first_name",
            "last_name",
            "credibility_score",
            "avatar_url",
            "dob",
            "bio",
            "diet",
            "food_preference",
            "created_at",
        ]

        read_only_fields = fields