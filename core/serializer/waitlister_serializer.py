from rest_framework import serializers

from core.models import Waitlister


class WaitlisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Waitlister
        fields = ["id", "name", "email", "created_at"]
        read_only_fields = ["id", "created_at"]
