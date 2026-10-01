from django.urls import path

from .views.refresh_tokens import RefreshAccessToken
from .views.signup_view import SignupView
from .views.login_view import LoginView
from .views.reset_password_view import ResetPasswordView
from .views.me_view import MeView
from .views.logout_view import LogoutView
from .views.delete_account_view import DeleteAccountView

urlpatterns = [
    path("refresh/",RefreshAccessToken.as_view(), name="get refresh token"),
    path("signup/", SignupView.as_view(), name="signup"),
    path("login/", LoginView.as_view(), name="login"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset password"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete account"),
]

