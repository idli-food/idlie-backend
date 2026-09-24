from rest_framework import serializers

from .services import PURPOSES


class SendOtpSerializer(serializers.Serializer):
    phone = serializers.CharField()
    purpose = serializers.ChoiceField(choices=list(PURPOSES))


class VerifyOtpSerializer(SendOtpSerializer):
    code = serializers.CharField(min_length=4, max_length=10)
