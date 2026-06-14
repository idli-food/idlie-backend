from django.urls import path
from .views.generate_upload_url import GenerateUploadUrlView
from .views.create_post import CreatePostView
from .views.post_services_view import LikePostView, PostCommentView, SavePostView, GetSavedPostView

urlpatterns = [
    path("content/upload-url/", GenerateUploadUrlView.as_view(), name="get upload url"),
    path("", CreatePostView.as_view(), name="create new post"),
    path("<int:post_id>/like/", LikePostView.as_view(), name="like post"),
    path("<int:post_id>/comment/", PostCommentView.as_view(), name="like post"),
    path("<int:post_id>/comment/<uuid:comment_id>/", PostCommentView.as_view(), name="post comment"),
    path("<int:post_id>/save/", SavePostView.as_view(), name="save post"),
    path("saved/me/", GetSavedPostView.as_view(), name="save post"),
]