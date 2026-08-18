from django.urls import path

from .views.create_hotel_view import CreateHotelView
from .authentication.views.signup import SignupView
from .views.hotel_test_view import HotelTestView
from .authentication.views.validate_otp import ValidateOTPView
from .authentication.views.login import SendLoginOTPView,ValidateLoginOTPView


urlpatterns = [
    path("create/", CreateHotelView.as_view(), name="create-hotel"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("test/", HotelTestView.as_view(), name="hotel-test"),
    path("validate-otp/", ValidateOTPView.as_view(), name="validate-otp"),
    path("login-otp/", SendLoginOTPView.as_view(), name="login-otp"),
    path("validate-login-otp/", ValidateLoginOTPView.as_view(), name="validate-login-otp"),


]
