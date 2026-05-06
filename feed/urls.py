from django.urls import path
from .views.feed_view import FeedView

urlpatterns = [
    path("", FeedView.as_view(),name="feed view"),
]