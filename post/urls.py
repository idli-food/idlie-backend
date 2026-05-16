from django.urls import path
from .views.generate_upload_url import GenerateUploadUrlView
from .views.create_post import CreatePostView
from .views.like_post import LikePostView

urlpatterns = [
    path("content/upload-url/", GenerateUploadUrlView.as_view(), name="get upload url"),
    path("", CreatePostView.as_view(), name="create new post"),
    path("<int:post_id>/like/", LikePostView.as_view(), name="like post"),

]