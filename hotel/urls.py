from django.urls import path

from .views.create_hotel_view import CreateHotelView
from .views.hotel_test_view import HotelTestView
from .views.hotel_profile_view import GetHotelProfileView
from .views.hotel_list_view import ListHotelsView
from .authentication.views.login import HotelLoginView
from .authentication.views.signup import SignupView
from .authentication.views.validate_otp import ValidateOTPView
from .authentication.views.password_reset import HotelResetPasswordView
from .authentication.views.token_refresh import RefreshAccessToken
from .views.hotel_service_views import UploadProfilePictureURLView
from .menu.views.create_menu import CreateMenuView
from .menu.views.menu_list import MenuListView
from .menu.views.menu_detail import MenuDetailView
from .menu.views.create_category import CreateMenuCategoryView
from .menu.views.category_detail import MenuCategoryDetailView
from .menu.views.create_fooditem import CreateFoodItemView
from .menu.views.fooditem_detail import FoodItemDetailView
from .menu.views.create_variant import CreateFoodItemVariantView
from .menu.views.variant_detail import FoodItemVariantDetailView
from .views.rating_view import CreateHotelRatingView, CreateHotelReviewView
from .views.nearest_hotel_view import NearestHotelView
from .views import admin_views
urlpatterns = [
    path("create/", CreateHotelView.as_view(), name="create-hotel"),
    path("signup/", SignupView.as_view(), name="hotel-signup"),
    path("validate-otp/", ValidateOTPView.as_view(), name="hotel-validate-otp"),
    path("login/", HotelLoginView.as_view(), name="hotel-login"),
    path("reset-password/", HotelResetPasswordView.as_view(), name="hotel-reset-password"),
    path('refresh-token/', RefreshAccessToken.as_view(), name='refresh-token'),
    path("profile/<int:hotel_id>/", GetHotelProfileView.as_view(), name="hotel-profile"),
    path("list/", ListHotelsView.as_view(), name="hotel-list"),
    path("nearest/", NearestHotelView.as_view(), name="nearest-hotel"),
    path("avatar-upload-url/", UploadProfilePictureURLView.as_view(), name="hotel-avatar-upload-url"),
    path("menu/", MenuListView.as_view(), name="menu-list"),
    path("menu/create/", CreateMenuView.as_view(), name="create-menu"),
    path("menu/<int:pk>/", MenuDetailView.as_view(), name="menu-detail"),
    path("menu/<int:menu_id>/category/create/", CreateMenuCategoryView.as_view(), name="create-menu-category"),
    path("menu/category/<int:pk>/", MenuCategoryDetailView.as_view(), name="menu-category-detail"),
    path("menu/category/<int:category_id>/item/create/", CreateFoodItemView.as_view(), name="create-food-item"),
    path("menu/item/<int:pk>/", FoodItemDetailView.as_view(), name="food-item-detail"),
    path("menu/item/<int:food_item_id>/variant/create/", CreateFoodItemVariantView.as_view(), name="create-food-item-variant"),
    path("menu/variant/<int:pk>/", FoodItemVariantDetailView.as_view(), name="food-item-variant-detail"),
    path("<int:hotel_id>/rating/", CreateHotelRatingView.as_view(), name="create-hotel-rating"),
    path("<int:hotel_id>/review/", CreateHotelReviewView.as_view(), name="create-hotel-review"),
    path("admin/login/", admin_views.AdminLoginView.as_view(), name="admin-login"),
    path("admin/hotels/", admin_views.AdminHotelListView.as_view(), name="admin-hotel-list"),
    path("admin/hotels/<int:pk>/", admin_views.AdminHotelDetailView.as_view(), name="admin-hotel-detail"),
    path("admin/hotels/<int:hotel_id>/menus/", admin_views.AdminHotelMenuListView.as_view(), name="admin-hotel-menus"),
    path("admin/hotels/<int:hotel_id>/menus/import/", admin_views.AdminHotelMenuImportView.as_view(), name="admin-hotel-menu-import"),
    path("admin/hotels/<int:hotel_id>/ratings/", admin_views.AdminHotelRatingListView.as_view(), name="admin-hotel-ratings"),
    path("admin/hotels/<int:hotel_id>/reviews/", admin_views.AdminHotelReviewListView.as_view(), name="admin-hotel-reviews"),
    path("admin/avatar-upload-url/", admin_views.AdminAvatarUploadURLView.as_view(), name="admin-avatar-upload-url"),
    path("admin/menus/<int:pk>/", admin_views.AdminMenuDetailView.as_view(), name="admin-menu-detail"),
    path("admin/menus/<int:menu_id>/categories/", admin_views.AdminCreateMenuCategoryView.as_view(), name="admin-create-category"),
    path("admin/categories/<int:pk>/", admin_views.AdminMenuCategoryDetailView.as_view(), name="admin-category-detail"),
    path("admin/categories/<int:category_id>/items/", admin_views.AdminCreateFoodItemView.as_view(), name="admin-create-food-item"),
    path("admin/items/<int:pk>/", admin_views.AdminFoodItemDetailView.as_view(), name="admin-food-item-detail"),
    path("admin/items/<int:food_item_id>/variants/", admin_views.AdminCreateFoodItemVariantView.as_view(), name="admin-create-variant"),
    path("admin/variants/<int:pk>/", admin_views.AdminFoodItemVariantDetailView.as_view(), name="admin-variant-detail"),
    path("admin/tags/", admin_views.AdminTagListView.as_view(), name="admin-tag-list"),
    path("admin/tags/<int:pk>/", admin_views.AdminTagDetailView.as_view(), name="admin-tag-detail"),
    path("admin/tags/<int:pk>/hotels/", admin_views.AdminTagHotelsView.as_view(), name="admin-tag-hotels"),
    path("admin/ratings/<int:pk>/", admin_views.AdminHotelRatingDetailView.as_view(), name="admin-rating-detail"),
    path("admin/reviews/<int:pk>/", admin_views.AdminHotelReviewDetailView.as_view(), name="admin-review-detail"),


]
