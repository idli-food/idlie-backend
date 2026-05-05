from django.urls import path,include
from .views.hello_world import HomeView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
]
