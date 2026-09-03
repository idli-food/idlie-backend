



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


class MenuListSerializer(serializers.ModelSerializer):
    category_count = serializers.SerializerMethodField()
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = [
            "id",
            "name",
            "is_active",
            "category_count",
            "item_count",
        ]

    def get_category_count(self, obj):
        return len(obj.categories.all())

    def get_item_count(self, obj):
        return sum(len(category.items.all()) for category in obj.categories.all())


class MenuCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuCategory
        fields = [
            "id",
            "name",
            "menu",
            "display_order",
        ]
        read_only_fields = ["id", "menu"]



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
        read_only_fields = ["id", "category"]

class FoodItemVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItemVariant
        fields = [
            "id",
            "food_item",
            "portion_name",
            "price",
            "is_available",
        ]
        read_only_fields = ["id", "food_item"]












class FoodItemVariantDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItemVariant
        fields = [
            "id",
            "portion_name",
            "price",
            "is_available",
        ]


class FoodItemDetailSerializer(serializers.ModelSerializer):
    variants = FoodItemVariantDetailSerializer(many=True, read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            "id",
            "name",
            "description",
            "image",
            "food_type",
            "is_active",
            "display_order",
            "variants",
        ]


class MenuCategoryDetailSerializer(serializers.ModelSerializer):
    items = FoodItemDetailSerializer(many=True, read_only=True)

    class Meta:
        model = MenuCategory
        fields = [
            "id",
            "name",
            "display_order",
            "items",
        ]


class MenuDetailSerializer(serializers.ModelSerializer):
    categories = MenuCategoryDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = [
            "id",
            "hotel",
            "name",
            "is_active",
            "categories",
        ]
