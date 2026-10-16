import requests
from django.contrib.auth import authenticate
from django.core.paginator import Paginator
from django.db.models import Q
from rest_framework import status
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from authentication.jwt.jwt_utils import create_access_token, create_refresh_token

from hotel.models import Hotel, Menu, MenuCategory, FoodItem, FoodItemVariant, HotelRating, HotelReview
from hotel.serializers.hotel_serializer import AdminHotelSerializer
from hotel.serializers.rating_serializer import HotelRatingSerializer, HotelReviewSerializer
from hotel.services.hotel_services import hotel_rating_summary
from hotel.menu.serializer.menu_serializer import (
    MainMenuSerializer,
    MenuListSerializer,
    MenuDetailSerializer,
    MenuImportSerializer,
    MenuCategorySerializer,
    FoodItemSerializer,
    FoodItemVariantSerializer,
)
from post.models import Tag
from user.serivices.user_service import get_avatar_upload_url
from core.services import places
from core.utils.api_response import success_response, error_response

ADMIN_HOTEL_PAGE_SIZE = 50


class IsStaffUser(BasePermission):
    # Hotel principals have no is_staff attribute, so getattr keeps them out
    def has_permission(self, request, view):
        return bool(getattr(request.user, "is_staff", False))


def not_found(message):
    return error_response(message=message, code=status.HTTP_404_NOT_FOUND)


def validation_error(errors):
    return error_response(message="Validation error", errors=errors, code=status.HTTP_400_BAD_REQUEST)


class AdminLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        username = (request.data.get("username") or "").strip()
        password = request.data.get("password") or ""

        if not username or not password:
            return error_response(message="username and password are required")

        # Same check as the Django admin login: active user, matching password, staff flag
        user = authenticate(request, username=username, password=password)
        if user is None:
            return error_response(message="Invalid credentials", code=status.HTTP_401_UNAUTHORIZED)

        if not user.is_staff:
            return error_response(message="This account isn't a staff account", code=status.HTTP_403_FORBIDDEN)

        return success_response(
            message="Login successful",
            data={
                "user": {"id": user.id, "username": user.username},
                "tokens": {"access": create_access_token(user.id), "refresh": create_refresh_token(user.id)},
            },
        )


class AdminHotelListView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        hotels = Hotel.objects.prefetch_related("tags").order_by("-created_at")

        query = request.GET.get("q", "").strip()
        if query:
            hotels = hotels.filter(
                Q(name__icontains=query)
                | Q(address__icontains=query)
                | Q(city__icontains=query)
                | Q(phone_number__icontains=query)
            )

        page = Paginator(hotels, ADMIN_HOTEL_PAGE_SIZE).get_page(request.GET.get("page"))

        return success_response(
            message="Hotels fetched successfully",
            data={
                "results": AdminHotelSerializer(page.object_list, many=True).data,
                "count": page.paginator.count,
                "page": page.number,
                "num_pages": page.paginator.num_pages,
            }
        )

    def post(self, request):
        serializer = AdminHotelSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        hotel = serializer.save()
        return success_response(
            message="Hotel created successfully",
            data=AdminHotelSerializer(hotel).data,
            code=status.HTTP_201_CREATED
        )


class AdminHotelDetailView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=pk)
        except Hotel.DoesNotExist:
            return not_found("Hotel not found")

        data = AdminHotelSerializer(hotel).data
        data.update(hotel_rating_summary(hotel))
        return success_response(message="Hotel fetched successfully", data=data)

    def patch(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=pk)
        except Hotel.DoesNotExist:
            return not_found("Hotel not found")

        serializer = AdminHotelSerializer(hotel, data=request.data, partial=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        serializer.save()
        return success_response(message="Hotel updated successfully", data=serializer.data)

    def delete(self, request, pk):
        try:
            hotel = Hotel.objects.get(id=pk)
        except Hotel.DoesNotExist:
            return not_found("Hotel not found")

        hotel.delete()
        return success_response(message="Hotel deleted successfully")


class AdminHotelFromLinkView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        link = (request.data.get("link") or "").strip()
        if not link:
            return error_response(message="link is required")

        try:
            data = places.from_maps_link(link)
        except requests.RequestException:
            return error_response(message="Fetching place from link failed", code=status.HTTP_502_BAD_GATEWAY)

        if data is None:
            return not_found("No place found for this link")

        return success_response(message="Place fetched successfully", data=data)


class AdminAvatarUploadURLView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request):
        result = get_avatar_upload_url(
            request.data.get("file_name"), request.data.get("content_type"), role="hotel"
        )
        return success_response(message="Profile picture upload URL generated", data=result)


class AdminHotelMenuListView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, hotel_id):
        menus = Menu.objects.filter(hotel_id=hotel_id).prefetch_related("categories__items")
        return success_response(
            message="Menus fetched successfully",
            data=MenuListSerializer(menus, many=True).data
        )

    def post(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return not_found("Hotel not found")

        serializer = MainMenuSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        menu = serializer.save(hotel=hotel)
        return success_response(
            message="Menu created successfully",
            data=MainMenuSerializer(menu).data,
            code=status.HTTP_201_CREATED
        )


class AdminHotelMenuImportView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, hotel_id):
        try:
            hotel = Hotel.objects.get(id=hotel_id)
        except Hotel.DoesNotExist:
            return not_found("Hotel not found")

        serializer = MenuImportSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        menu = serializer.save(hotel=hotel)
        menu = Menu.objects.prefetch_related("categories__items__variants").get(id=menu.id)
        return success_response(
            message="Menu imported successfully",
            data=MenuDetailSerializer(menu).data,
            code=status.HTTP_201_CREATED
        )


class AdminMenuDetailView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, pk):
        try:
            menu = Menu.objects.prefetch_related("categories__items__variants").get(id=pk)
        except Menu.DoesNotExist:
            return not_found("Menu not found")

        return success_response(message="Menu retrieved successfully", data=MenuDetailSerializer(menu).data)

    def patch(self, request, pk):
        try:
            menu = Menu.objects.get(id=pk)
        except Menu.DoesNotExist:
            return not_found("Menu not found")

        serializer = MainMenuSerializer(menu, data=request.data, partial=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        serializer.save()
        return success_response(message="Menu updated successfully", data=serializer.data)

    def delete(self, request, pk):
        try:
            menu = Menu.objects.get(id=pk)
        except Menu.DoesNotExist:
            return not_found("Menu not found")

        menu.delete()
        return success_response(message="Menu deleted successfully")


class AdminCreateMenuCategoryView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, menu_id):
        try:
            menu = Menu.objects.get(id=menu_id)
        except Menu.DoesNotExist:
            return not_found("Menu not found")

        serializer = MenuCategorySerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        category = serializer.save(menu=menu)
        return success_response(
            message="Menu category created successfully",
            data=MenuCategorySerializer(category).data,
            code=status.HTTP_201_CREATED
        )


class AdminMenuCategoryDetailView(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        try:
            category = MenuCategory.objects.get(id=pk)
        except MenuCategory.DoesNotExist:
            return not_found("Menu category not found")

        serializer = MenuCategorySerializer(category, data=request.data, partial=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        serializer.save()
        return success_response(message="Menu category updated successfully", data=serializer.data)

    def delete(self, request, pk):
        try:
            category = MenuCategory.objects.get(id=pk)
        except MenuCategory.DoesNotExist:
            return not_found("Menu category not found")

        category.delete()
        return success_response(message="Menu category deleted successfully")


class AdminCreateFoodItemView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, category_id):
        try:
            category = MenuCategory.objects.get(id=category_id)
        except MenuCategory.DoesNotExist:
            return not_found("Menu category not found")

        serializer = FoodItemSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        food_item = serializer.save(category=category)
        return success_response(
            message="Food item created successfully",
            data=FoodItemSerializer(food_item).data,
            code=status.HTTP_201_CREATED
        )


class AdminFoodItemDetailView(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        try:
            food_item = FoodItem.objects.get(id=pk)
        except FoodItem.DoesNotExist:
            return not_found("Food item not found")

        serializer = FoodItemSerializer(food_item, data=request.data, partial=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        serializer.save()
        return success_response(message="Food item updated successfully", data=serializer.data)

    def delete(self, request, pk):
        try:
            food_item = FoodItem.objects.get(id=pk)
        except FoodItem.DoesNotExist:
            return not_found("Food item not found")

        food_item.delete()
        return success_response(message="Food item deleted successfully")


class AdminCreateFoodItemVariantView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, food_item_id):
        try:
            food_item = FoodItem.objects.get(id=food_item_id)
        except FoodItem.DoesNotExist:
            return not_found("Food item not found")

        serializer = FoodItemVariantSerializer(data=request.data)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        variant = serializer.save(food_item=food_item)
        return success_response(
            message="Food item variant created successfully",
            data=FoodItemVariantSerializer(variant).data,
            code=status.HTTP_201_CREATED
        )


class AdminFoodItemVariantDetailView(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        try:
            variant = FoodItemVariant.objects.get(id=pk)
        except FoodItemVariant.DoesNotExist:
            return not_found("Food item variant not found")

        serializer = FoodItemVariantSerializer(variant, data=request.data, partial=True)
        if not serializer.is_valid():
            return validation_error(serializer.errors)

        serializer.save()
        return success_response(message="Food item variant updated successfully", data=serializer.data)

    def delete(self, request, pk):
        try:
            variant = FoodItemVariant.objects.get(id=pk)
        except FoodItemVariant.DoesNotExist:
            return not_found("Food item variant not found")

        variant.delete()
        return success_response(message="Food item variant deleted successfully")


class AdminTagListView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request):
        tags = Tag.objects.order_by("name").values("id", "name")
        return success_response(message="Tags fetched successfully", data=list(tags))

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        if not name:
            return validation_error({"name": ["This field is required."]})
        if Tag.objects.filter(name__iexact=name).exists():
            return validation_error({"name": ["A tag with this name already exists."]})

        tag = Tag.objects.create(name=name)
        return success_response(
            message="Tag created successfully",
            data={"id": tag.id, "name": tag.name},
            code=status.HTTP_201_CREATED
        )


class AdminTagDetailView(APIView):
    permission_classes = [IsStaffUser]

    def patch(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            return not_found("Tag not found")

        name = (request.data.get("name") or "").strip()
        if not name:
            return validation_error({"name": ["This field is required."]})
        if Tag.objects.filter(name__iexact=name).exclude(id=pk).exists():
            return validation_error({"name": ["A tag with this name already exists."]})

        tag.name = name
        tag.save()
        return success_response(message="Tag updated successfully", data={"id": tag.id, "name": tag.name})

    def delete(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            return not_found("Tag not found")

        tag.delete()
        return success_response(message="Tag deleted successfully")


class AdminTagHotelsView(APIView):
    permission_classes = [IsStaffUser]

    def post(self, request, pk):
        try:
            tag = Tag.objects.get(id=pk)
        except Tag.DoesNotExist:
            return not_found("Tag not found")

        hotel_ids = request.data.get("hotel_ids")
        if not isinstance(hotel_ids, list) or not hotel_ids or not all(isinstance(i, int) for i in hotel_ids):
            return validation_error({"hotel_ids": ["Provide a non-empty list of hotel ids."]})

        hotels = list(Hotel.objects.filter(id__in=hotel_ids))
        tag.hotels.add(*hotels)
        return success_response(
            message="Tag added to hotels successfully",
            data={"tag": {"id": tag.id, "name": tag.name}, "hotel_count": len(hotels)}
        )


class AdminHotelRatingListView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, hotel_id):
        ratings = HotelRating.objects.filter(hotel_id=hotel_id).select_related("user__profile").order_by("-created_at")
        return success_response(
            message="Ratings fetched successfully",
            data=HotelRatingSerializer(ratings, many=True).data
        )


class AdminHotelRatingDetailView(APIView):
    permission_classes = [IsStaffUser]

    def delete(self, request, pk):
        try:
            rating = HotelRating.objects.get(id=pk)
        except HotelRating.DoesNotExist:
            return not_found("Rating not found")

        rating.delete()
        return success_response(message="Rating deleted successfully")


class AdminHotelReviewListView(APIView):
    permission_classes = [IsStaffUser]

    def get(self, request, hotel_id):
        reviews = HotelReview.objects.filter(hotel_id=hotel_id).select_related("user__profile").order_by("-created_at")
        return success_response(
            message="Reviews fetched successfully",
            data=HotelReviewSerializer(reviews, many=True).data
        )


class AdminHotelReviewDetailView(APIView):
    permission_classes = [IsStaffUser]

    def delete(self, request, pk):
        try:
            review = HotelReview.objects.get(id=pk)
        except HotelReview.DoesNotExist:
            return not_found("Review not found")

        review.delete()
        return success_response(message="Review deleted successfully")
