from django.shortcuts import render

from django.urls import path,include

# Create your views here.
from .views.login_view import LoginView
from .views.profle_view import ProfileView

urlpatterns = [

path("login/",LoginView.as_view(),name="login view"),
path("profile/",ProfileView.as_view(),name="login view")

]