from django.urls import path

from .views.create_hotel_view import CreateHotelView
from .authentication.views.signup import SignupView
from .views.hotel_test_view import HotelTestView
from .views.get_hotel_profile import GetHotelProfileView
from .authentication.views.validate_otp import ValidateOTPView
from .authentication.views.login import SendLoginOTPView,ValidateLoginOTPView
from .authentication.views.token_refresh import RefreshAccessToken

urlpatterns = [
    path("create/", CreateHotelView.as_view(), name="create-hotel"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("validate-otp/", ValidateOTPView.as_view(), name="validate-otp"),
    path("login-otp/", SendLoginOTPView.as_view(), name="login-otp"),
    path('refresh-token/', RefreshAccessToken.as_view(), name='refresh-token'),
    path("validate-login-otp/", ValidateLoginOTPView.as_view(), name="validate-login-otp"),
    path("profile/", GetHotelProfileView.as_view(), name="hotel-profile"),


]
