from django.urls import path
from .views.feed_view import FeedView
from .views.explore_view import ExplorePageView
from .views.instant_feed_view import InstantFeedView

urlpatterns = [
    path("", FeedView.as_view(),name="feed view"),
    path("explore/", ExplorePageView.as_view(),name="explore view"),
    path("instant/", InstantFeedView.as_view(),name="instant feed view"),

]