from django.urls import path

from .views.get_otp_view import SendOtpView
from .views.validate_otp import ValidateOTPView
urlpatterns = [
    path("get-otp/", SendOtpView.as_view(),name="get phone number"),
    path("validate-otp/", ValidateOTPView.as_view(),name="get phone number"),

]