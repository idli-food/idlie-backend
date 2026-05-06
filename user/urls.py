from django.urls import path,include
from .views.add_user_view import AddUserView
urlpatterns = [
    path('', AddUserView.as_view(), name='home')
    

]
