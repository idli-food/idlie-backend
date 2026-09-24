from django.utils import timezone
from rest_framework import serializers
from hotel.models import Hotel
from rest_framework_gis.fields import GeometryField
from post.services import post_service





class CreateHotelSerializer(serializers.ModelSerializer):
    location = GeometryField(required=False)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "address",
            "city",
            "phone_number",
            "email",
            "description",
            "location",
            "location_link",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        hotel = Hotel(**validated_data)
        hotel.set_password(password)
        hotel.phone_verified = True
        hotel.phone_verified_at = timezone.now()
        hotel.save()
        return hotel


class HotelProfileSerializer(serializers.ModelSerializer):
    location = GeometryField(required=False)

    class Meta:
        model = Hotel
        fields = [
            "name",
            "phone_number",
            "avatar",
            "address",
            "location",
            "location_link",
            "phone_verified",
        ]
        read_only_fields = ["phone_verified"]

    def update(self, instance, validated_data):
        avatar = validated_data.pop("avatar", None)

        if avatar is not None:
            instance.avatar = post_service.get_s3_public_url(avatar)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance