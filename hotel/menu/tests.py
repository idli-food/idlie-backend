from decimal import Decimal

from rest_framework.test import APITestCase
from rest_framework import status

from hotel.models import Hotel, Menu, MenuCategory, FoodItem, FoodItemVariant
from hotel.authentication.services.jwt.jwt_utils import create_access_token


def auth_header(hotel_id):
    token = create_access_token(hotel_id)
    return {"HTTP_AUTHORIZATION": f"Bearer {token}"}


class MenuAPITestCase(APITestCase):
    """End-to-end coverage for menu / category / food item / variant CRUD."""

    def setUp(self):
        self.hotel = Hotel.objects.create(
            name="Idli House",
            address="MG Road",
            city="Trivandrum",
            phone_number="9999999999",
            email="idli@example.com",
        )
        self.other_hotel = Hotel.objects.create(
            name="Other Hotel",
            address="Other Street",
            city="Kochi",
            phone_number="8888888888",
            email="other@example.com",
        )
        self.headers = auth_header(self.hotel.id)
        self.other_headers = auth_header(self.other_hotel.id)

    # ---------- Menu ----------

    def test_create_menu_requires_auth(self):
        response = self.client.post("/hotel/menu/create/", {"name": "Breakfast"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_menu_success(self):
        response = self.client.post(
            "/hotel/menu/create/",
            {"name": "Breakfast", "is_active": True},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["data"]["name"], "Breakfast")
        self.assertEqual(Menu.objects.count(), 1)
        self.assertEqual(Menu.objects.first().hotel_id, self.hotel.id)

    def test_create_menu_missing_name(self):
        response = self.client.post(
            "/hotel/menu/create/", {}, format="json", **self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_menus_scoped_to_hotel(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin", display_order=1)
        FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        FoodItem.objects.create(category=category, name="Vada", food_type="veg")
        Menu.objects.create(hotel=self.other_hotel, name="Other Menu")

        response = self.client.get("/hotel/menu/", **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Breakfast")
        self.assertEqual(data[0]["category_count"], 1)
        self.assertEqual(data[0]["item_count"], 2)

    def test_list_menus_requires_auth(self):
        response = self.client.get("/hotel/menu/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_menu_detail_with_nested_data(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin", display_order=1)
        item = FoodItem.objects.create(
            category=category, name="Idli", food_type="veg", description="Soft idli"
        )
        FoodItemVariant.objects.create(food_item=item, portion_name="Regular", price=Decimal("40.00"))

        response = self.client.get(f"/hotel/menu/{menu.id}/", **self.headers)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data["data"]
        self.assertEqual(data["name"], "Breakfast")
        self.assertEqual(len(data["categories"]), 1)
        self.assertEqual(data["categories"][0]["name"], "Tiffin")
        self.assertEqual(len(data["categories"][0]["items"]), 1)
        self.assertEqual(data["categories"][0]["items"][0]["name"], "Idli")
        self.assertEqual(len(data["categories"][0]["items"][0]["variants"]), 1)
        self.assertEqual(data["categories"][0]["items"][0]["variants"][0]["portion_name"], "Regular")

    def test_get_menu_detail_not_found(self):
        response = self.client.get("/hotel/menu/999999/", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_menu_detail_other_hotel_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.get(f"/hotel/menu/{menu.id}/", **self.other_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_menu(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.patch(
            f"/hotel/menu/{menu.id}/",
            {"name": "Lunch", "is_active": False},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        menu.refresh_from_db()
        self.assertEqual(menu.name, "Lunch")
        self.assertFalse(menu.is_active)

    def test_patch_menu_other_hotel_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.patch(
            f"/hotel/menu/{menu.id}/", {"name": "Hijack"}, format="json", **self.other_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        menu.refresh_from_db()
        self.assertEqual(menu.name, "Breakfast")

    def test_delete_menu(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.delete(f"/hotel/menu/{menu.id}/", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Menu.objects.count(), 0)

    def test_delete_menu_other_hotel_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.delete(f"/hotel/menu/{menu.id}/", **self.other_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(Menu.objects.count(), 1)

    # ---------- Category ----------

    def test_create_category_success(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.post(
            f"/hotel/menu/{menu.id}/category/create/",
            {"name": "Tiffin", "display_order": 1},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MenuCategory.objects.count(), 1)
        self.assertEqual(MenuCategory.objects.first().menu_id, menu.id)

    def test_create_category_menu_not_found(self):
        response = self.client.post(
            "/hotel/menu/999999/category/create/",
            {"name": "Tiffin"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_category_on_other_hotels_menu_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        response = self.client.post(
            f"/hotel/menu/{menu.id}/category/create/",
            {"name": "Hijack"},
            format="json",
            **self.other_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_category(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        response = self.client.patch(
            f"/hotel/menu/category/{category.id}/",
            {"name": "Snacks", "display_order": 2},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, "Snacks")
        self.assertEqual(category.display_order, 2)

    def test_delete_category(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        response = self.client.delete(f"/hotel/menu/category/{category.id}/", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(MenuCategory.objects.count(), 0)

    def test_delete_category_other_hotel_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        response = self.client.delete(
            f"/hotel/menu/category/{category.id}/", **self.other_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(MenuCategory.objects.count(), 1)

    # ---------- Food item ----------

    def test_create_food_item_success(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        response = self.client.post(
            f"/hotel/menu/category/{category.id}/item/create/",
            {
                "name": "Idli",
                "description": "Soft idli",
                "food_type": "veg",
                "is_active": True,
                "display_order": 1,
            },
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FoodItem.objects.count(), 1)
        self.assertEqual(FoodItem.objects.first().category_id, category.id)

    def test_create_food_item_invalid_food_type(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        response = self.client.post(
            f"/hotel/menu/category/{category.id}/item/create/",
            {"name": "Idli", "food_type": "invalid"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_food_item_category_not_found(self):
        response = self.client.post(
            "/hotel/menu/category/999999/item/create/",
            {"name": "Idli", "food_type": "veg"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_food_item(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        response = self.client.patch(
            f"/hotel/menu/item/{item.id}/",
            {"name": "Mini Idli", "is_active": False},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        item.refresh_from_db()
        self.assertEqual(item.name, "Mini Idli")
        self.assertFalse(item.is_active)

    def test_delete_food_item(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        response = self.client.delete(f"/hotel/menu/item/{item.id}/", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FoodItem.objects.count(), 0)

    def test_delete_food_item_other_hotel_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        response = self.client.delete(f"/hotel/menu/item/{item.id}/", **self.other_headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(FoodItem.objects.count(), 1)

    # ---------- Variant ----------

    def test_create_variant_success(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        response = self.client.post(
            f"/hotel/menu/item/{item.id}/variant/create/",
            {"portion_name": "Regular", "price": "40.00", "is_available": True},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FoodItemVariant.objects.count(), 1)
        self.assertEqual(FoodItemVariant.objects.first().food_item_id, item.id)

    def test_create_variant_missing_price(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        response = self.client.post(
            f"/hotel/menu/item/{item.id}/variant/create/",
            {"portion_name": "Regular"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_variant_food_item_not_found(self):
        response = self.client.post(
            "/hotel/menu/item/999999/variant/create/",
            {"portion_name": "Regular", "price": "40.00"},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_variant(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        variant = FoodItemVariant.objects.create(
            food_item=item, portion_name="Regular", price=Decimal("40.00")
        )
        response = self.client.patch(
            f"/hotel/menu/variant/{variant.id}/",
            {"price": "50.00", "is_available": False},
            format="json",
            **self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        variant.refresh_from_db()
        self.assertEqual(variant.price, Decimal("50.00"))
        self.assertFalse(variant.is_available)

    def test_delete_variant(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        variant = FoodItemVariant.objects.create(
            food_item=item, portion_name="Regular", price=Decimal("40.00")
        )
        response = self.client.delete(f"/hotel/menu/variant/{variant.id}/", **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(FoodItemVariant.objects.count(), 0)

    def test_delete_variant_other_hotel_forbidden(self):
        menu = Menu.objects.create(hotel=self.hotel, name="Breakfast")
        category = MenuCategory.objects.create(menu=menu, name="Tiffin")
        item = FoodItem.objects.create(category=category, name="Idli", food_type="veg")
        variant = FoodItemVariant.objects.create(
            food_item=item, portion_name="Regular", price=Decimal("40.00")
        )
        response = self.client.delete(
            f"/hotel/menu/variant/{variant.id}/", **self.other_headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(FoodItemVariant.objects.count(), 1)

    # ---------- Full flow ----------

    def test_full_menu_creation_flow(self):
        menu_response = self.client.post(
            "/hotel/menu/create/", {"name": "Full Menu"}, format="json", **self.headers
        )
        menu_id = menu_response.data["data"]["id"]

        category_response = self.client.post(
            f"/hotel/menu/{menu_id}/category/create/",
            {"name": "Tiffin"},
            format="json",
            **self.headers,
        )
        category_id = category_response.data["data"]["id"]

        item_response = self.client.post(
            f"/hotel/menu/category/{category_id}/item/create/",
            {"name": "Idli", "food_type": "veg"},
            format="json",
            **self.headers,
        )
        item_id = item_response.data["data"]["id"]

        variant_response = self.client.post(
            f"/hotel/menu/item/{item_id}/variant/create/",
            {"portion_name": "Regular", "price": "40.00"},
            format="json",
            **self.headers,
        )
        self.assertEqual(variant_response.status_code, status.HTTP_201_CREATED)

        detail_response = self.client.get(f"/hotel/menu/{menu_id}/", **self.headers)
        data = detail_response.data["data"]
        self.assertEqual(len(data["categories"]), 1)
        self.assertEqual(len(data["categories"][0]["items"]), 1)
        self.assertEqual(len(data["categories"][0]["items"][0]["variants"]), 1)
