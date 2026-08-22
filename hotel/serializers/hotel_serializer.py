from rest_framework import serializers
from hotel.models import Hotel, HotelProfile
from rest_framework_gis.fields import GeometryField
from post.services import post_service





class CreateHotelSerializer(serializers.ModelSerializer):
    location = GeometryField(required=False)

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
            "location"
        ]


class HotelProfileSerializer(serializers.ModelSerializer):
    location = GeometryField(required=False)
    bio = serializers.CharField(source="profile.bio", default=None, allow_null=True, required=False)
    nof_post = serializers.IntegerField(source="profile.nof_post", default=0, read_only=True)

    class Meta:
        model = Hotel
        fields = [
            "name",
            "phone_number",
            "bio",
            "avatar",
            "location",
            "nof_post",
        ]

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", None)
        avatar = validated_data.pop("avatar", None)

        if avatar is not None:
            instance.avatar = post_service.get_s3_public_url(avatar)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile, _ = HotelProfile.objects.get_or_create(Hotel=instance)
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance