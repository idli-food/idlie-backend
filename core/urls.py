from django.urls import path,include
from .views.hello_world import HomeView
from .views.places_view import PlacesAutocompleteView, PlaceDetailsView
from .views.waitlist_view import WaitlistView

urlpatterns = [
    path('home/', HomeView.as_view(), name='home'),
    path('places/autocomplete/', PlacesAutocompleteView.as_view(), name='places-autocomplete'),
    path('places/details/', PlaceDetailsView.as_view(), name='place-details'),
    path('waitlist/', WaitlistView.as_view(), name='waitlist'),
]
