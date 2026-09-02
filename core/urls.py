from django.urls import path,include
from .views.hello_world import HomeView
from .views.places_view import PlacesAutocompleteView, PlaceDetailsView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('places/autocomplete/', PlacesAutocompleteView.as_view(), name='places-autocomplete'),
    path('places/details/', PlaceDetailsView.as_view(), name='place-details'),
]
