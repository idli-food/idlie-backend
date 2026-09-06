from django.urls import path
from .views.profle_view import ProfileView
from .views.complete_profile_view import CompleteProfileView
from .views.avatar_upload_url_view import AvatarUploadUrlView
from .views.my_posts_view import MyPostsView
from .views.user_profile_view import UserProfileView
from .views.user_posts_view import UserPostsView



urlpatterns = [
    path("posts/me/", MyPostsView.as_view(), name="my posts"),
    path("posts/<int:user_id>/", UserPostsView.as_view(), name="user posts"),
    path("profile/", ProfileView.as_view(), name="profile view"),
    path("profile/<int:user_id>/", UserProfileView.as_view(), name="user profile view"),
    path("profile/complete/", CompleteProfileView.as_view(), name="complete profile"),
    path("avatar-upload-url/", AvatarUploadUrlView.as_view(), name="avatar upload url"),
]