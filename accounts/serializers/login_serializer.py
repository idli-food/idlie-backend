from rest_framework import serializers
from ..auth.login_auth import authenticate_user


class LoginSerializer(serializers.Serializer):
    identifier = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = authenticate_user(identifier, password)

        if not user:
            raise serializers.ValidationError(
                "Invalid credentials"
            )

        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled"
            )

        attrs["user"] = user
        return attrs