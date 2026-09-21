from django.urls import path

from .views import AddCoinsView, CoinsCountView, ReduceCoinsView

urlpatterns = [
    path('count/', CoinsCountView.as_view(), name='coins-count'),
    path('add/', AddCoinsView.as_view(), name='coins-add'),
    path('reduce/', ReduceCoinsView.as_view(), name='coins-reduce'),
]
