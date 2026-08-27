from django.urls import path

from .views.create_hotel_view import CreateHotelView
from .authentication.views.signup import SignupView
from .views.hotel_test_view import HotelTestView
from .views.hotel_profile_view import GetHotelProfileView
from .views.hotel_list_view import ListHotelsView
from .authentication.views.validate_otp import ValidateOTPView
from .authentication.views.login import SendLoginOTPView,ValidateLoginOTPView
from .authentication.views.token_refresh import RefreshAccessToken
from .views.hotel_service_views import UploadProfilePictureURLView
from .menu.views.create_menu import CreateMenuView
from .menu.views.menu_detail import MenuDetailView
from .menu.views.create_category import CreateMenuCategoryView
from .menu.views.category_detail import MenuCategoryDetailView
from .menu.views.create_fooditem import CreateFoodItemView
from .menu.views.fooditem_detail import FoodItemDetailView
from .menu.views.create_variant import CreateFoodItemVariantView
from .menu.views.variant_detail import FoodItemVariantDetailView
from .views.rating_view import CreateHotelRatingView, CreateHotelReviewView
urlpatterns = [
    path("create/", CreateHotelView.as_view(), name="create-hotel"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("validate-otp/", ValidateOTPView.as_view(), name="validate-otp"),
    path("login-otp/", SendLoginOTPView.as_view(), name="login-otp"),
    path('refresh-token/', RefreshAccessToken.as_view(), name='refresh-token'),
    path("validate-login-otp/", ValidateLoginOTPView.as_view(), name="validate-login-otp"),
    path("profile/<int:hotel_id>/", GetHotelProfileView.as_view(), name="hotel-profile"),
    path("list/", ListHotelsView.as_view(), name="hotel-list"),
    path("avatar-upload-url/", UploadProfilePictureURLView.as_view(), name="hotel-avatar-upload-url"),
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


]
