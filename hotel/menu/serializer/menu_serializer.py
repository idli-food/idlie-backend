



from rest_framework import serializers
from hotel.models import Menu,MenuCategory,FoodItem,FoodItemVariant
















class MainMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = [
            "id",
            "hotel",
            "name",
            "is_active",
        ]
        read_only_fields = ["id", "hotel"]


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = [
            "id",
            "name",
            "menu",
            "display_order",
        ]



class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            "id",
            "category",
            "name",
            "description",
            "image",
            "food_type",
            "is_active",
            "display_order",
        ]

class FoodItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItemVariant
        fields = [
            "id",
            "food_item",
            "name",
            "price",
            "portion_size",
            "is_available",
        ]