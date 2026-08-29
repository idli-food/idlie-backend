from django.urls import path

from .views.get_otp_view import SendOtpView
from .views.validate_otp import ValidateOTPView
from .views.refresh_tokens import RefreshAccessToken
from .views.google_auth_view import GoogleLoginView, GoogleCallbackView, GoogleCompleteView
from .views.me_view import MeView
from .views.logout_view import LogoutView
from accounts.views.login_view import LoginView

urlpatterns = [
    path("get-otp/", SendOtpView.as_view(),name="get phone number"),
    path("validate-otp/", ValidateOTPView.as_view(),name="get phone number"),
    path("refresh/",RefreshAccessToken.as_view(), name="get refresh token"),
    path("login/", LoginView.as_view(), name="login"),
    path("google/login/", GoogleLoginView.as_view(), name="google login"),
    path("google/callback/", GoogleCallbackView.as_view(), name="google callback"),
    path("google/complete/", GoogleCompleteView.as_view(), name="google complete"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

