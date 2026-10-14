



from django.db import transaction
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


class FoodItemImportSerializer(FoodItemSerializer):
    variants = FoodItemVariantSerializer(many=True, required=False)

    class Meta(FoodItemSerializer.Meta):
        fields = FoodItemSerializer.Meta.fields + ["variants"]


class MenuCategoryImportSerializer(MenuCategorySerializer):
    items = FoodItemImportSerializer(many=True, required=False)

    class Meta(MenuCategorySerializer.Meta):
        fields = MenuCategorySerializer.Meta.fields + ["items"]


class MenuImportSerializer(MainMenuSerializer):
    categories = MenuCategoryImportSerializer(many=True, required=False)

    class Meta(MainMenuSerializer.Meta):
        fields = MainMenuSerializer.Meta.fields + ["categories"]

    def create(self, validated_data):
        categories = validated_data.pop("categories", [])
        with transaction.atomic():
            menu = Menu.objects.create(**validated_data)
            for category_data in categories:
                items = category_data.pop("items", [])
                category = MenuCategory.objects.create(menu=menu, **category_data)
                for item_data in items:
                    variants = item_data.pop("variants", [])
                    food_item = FoodItem.objects.create(category=category, **item_data)
                    for variant_data in variants:
                        FoodItemVariant.objects.create(food_item=food_item, **variant_data)
        return menu
