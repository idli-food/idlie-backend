from django.urls import path

from .views.get_otp_view import SendOtpView
from .views.validate_otp import ValidateOTPView
from .views.refresh_tokens import RefreshAccessToken

urlpatterns = [
    path("get-otp/", SendOtpView.as_view(),name="get phone number"),
    path("validate-otp/", ValidateOTPView.as_view(),name="get phone number"),
    path("/refresh/",RefreshAccessToken.as_view(), name="get refresh token")

]

