from django.urls import path
from .views.generate_upload_url import GenerateUploadUrlView

urlpatterns = [
    path("content/upload-url/", GenerateUploadUrlView.as_view(), name="get upload url"),
]