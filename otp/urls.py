from django.urls import path

from .views import SendOtpView, VerifyOtpView

urlpatterns = [
    path("send/", SendOtpView.as_view(), name="otp-send"),
    path("verify/", VerifyOtpView.as_view(), name="otp-verify"),
]
