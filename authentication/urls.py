from django.urls import path

from .views.refresh_tokens import RefreshAccessToken
from .views.signup_view import SignupView
from .views.me_view import MeView
from .views.logout_view import LogoutView

urlpatterns = [
    path("refresh/",RefreshAccessToken.as_view(), name="get refresh token"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
]

