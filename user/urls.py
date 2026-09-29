from django.urls import path,include
from .views.user_detail_view import UserDetailView
urlpatterns = [
    path('me/details/', UserDetailView.as_view(), name='user-detail-view'),
    

]
