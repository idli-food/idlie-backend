from django.utils import timezone
from rest_framework import serializers
from hotel.models import Hotel, HotelCuisine, HotelService, HotelFacility, HotelDish, HotelSession
from rest_framework_gis.fields import GeometryField
from post.services import post_service


# request key -> (model, name field); sent/returned as plain string lists
HOTEL_LISTS = {
    "cuisines": (HotelCuisine, "cuisine_name"),
    "services": (HotelService, "service_name"),
    "facilities": (HotelFacility, "facility_name"),
    "dishes": (HotelDish, "dish_name"),
}


def pop_hotel_lists(validated_data):
    return {key: validated_data.pop(key) for key in HOTEL_LISTS if key in validated_data}


def set_hotel_lists(hotel, lists):
    for key, names in lists.items():
        model, field = HOTEL_LISTS[key]
        model.objects.filter(hotel=hotel).delete()
        model.objects.bulk_create([model(hotel=hotel, **{field: name}) for name in names])


def get_hotel_lists(hotel):
    return {
        key: list(getattr(hotel, key).values_list(field, flat=True))
        for key, (model, field) in HOTEL_LISTS.items()
    }


class HotelSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HotelSession
        fields = ["day", "start_time", "end_time"]





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
    cuisines = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)
    services = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)
    facilities = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)
    dishes = serializers.ListField(child=serializers.CharField(max_length=150), required=False, write_only=True)
    sessions = HotelSessionSerializer(many=True, required=False)

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
            "price_min",
            "price_max",
            "sessions",
            "atmosphere",
            "best_for",
            "cuisines",
            "services",
            "facilities",
            "dishes",
        ]
        read_only_fields = ["phone_verified"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(get_hotel_lists(instance))
        return data

    def update(self, instance, validated_data):
        avatar = validated_data.pop("avatar", None)
        lists = pop_hotel_lists(validated_data)
        sessions = validated_data.pop("sessions", None)

        if avatar is not None:
            instance.avatar = post_service.get_s3_public_url(avatar)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        set_hotel_lists(instance, lists)
        if sessions is not None:
            HotelSession.objects.filter(hotel=instance).delete()
            HotelSession.objects.bulk_create([HotelSession(hotel=instance, **s) for s in sessions])

        return instance

class AdminHotelSerializer(serializers.ModelSerializer):
    location = GeometryField(required=False, allow_null=True)
    password = serializers.CharField(write_only=True, min_length=6, required=False)
    # Accepts a full URL or an S3 key returned by the avatar upload URL endpoint
    avatar = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    cuisines = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)
    services = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)
    facilities = serializers.ListField(child=serializers.CharField(max_length=100), required=False, write_only=True)
    dishes = serializers.ListField(child=serializers.CharField(max_length=150), required=False, write_only=True)
    sessions = HotelSessionSerializer(many=True, required=False)

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
            "place_id",
            "avatar",
            "is_active",
            "phone_verified",
            "tags",
            "created_at",
            "updated_at",
            "password",
            "price_min",
            "price_max",
            "sessions",
            "atmosphere",
            "best_for",
            "cuisines",
            "services",
            "facilities",
            "dishes",
        ]
        read_only_fields = ["id", "phone_verified", "created_at", "updated_at"]

    def validate_avatar(self, value):
        if value and not value.startswith("http"):
            return post_service.get_s3_public_url(value)
        return value or None

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.update(get_hotel_lists(instance))
        return data

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        lists = pop_hotel_lists(validated_data)
        sessions = validated_data.pop("sessions", [])
        hotel = super().create(validated_data)
        if password:
            hotel.set_password(password)
            hotel.save()
        set_hotel_lists(hotel, lists)
        HotelSession.objects.bulk_create([HotelSession(hotel=hotel, **s) for s in sessions])
        return hotel

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        lists = pop_hotel_lists(validated_data)
        sessions = validated_data.pop("sessions", None)
        if password:
            instance.set_password(password)
        hotel = super().update(instance, validated_data)
        set_hotel_lists(hotel, lists)
        if sessions is not None:
            HotelSession.objects.filter(hotel=hotel).delete()
            HotelSession.objects.bulk_create([HotelSession(hotel=hotel, **s) for s in sessions])
        return hotel
