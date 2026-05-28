from django.urls import path
from .views.feed_view import FeedView
from .views.explore_view import ExplorePageView

urlpatterns = [
    path("", FeedView.as_view(),name="feed view"),
    path("", ExplorePageView.as_view(),name="explore view"),

]