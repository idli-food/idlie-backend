from django.urls import path,include
from .views.add_user_view import AddUserView
from .views.user_detail_view import UserDetailView
urlpatterns = [
    path('', AddUserView.as_view(), name='home'),
    path('me/details/', UserDetailView.as_view(), name='user-detail-view'),
    

]
