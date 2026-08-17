from rest_framework import serializers
from hotel.models import Hotel
from rest_framework_gis.fields import GeometryField





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