


from rest_framework import serializers
from ..models import User,UserProfile

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
            username=validate_data['username'],
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
            "created_at",
        ]

        read_only_fields = fields

class UserDetailViewSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = UserProfile
        fields = ['username','name','avatar','bio','dob','diet','food_preference','location']
