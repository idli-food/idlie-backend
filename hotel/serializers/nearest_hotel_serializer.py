from rest_framework import serializers
from hotel.models import Hotel


class NearestHotelRequestSerializer(serializers.Serializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()


class NearestHotelSerializer(serializers.ModelSerializer):
    distance_m = serializers.SerializerMethodField()

    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "address",
            "city",
            "phone_number",
            "avatar",
            "location_link",
            "distance_m",
        ]

    def get_distance_m(self, obj):
        return obj.distance.m
