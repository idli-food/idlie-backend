from django.core.management.base import BaseCommand
from hotel.models import Hotel
from post.models import Tag

CUISINES = [
    "American",
    "Arabic",
    "Bakery",
    "Beverages",
    "Biryani",
    "Café",
    "Chinese",
    "Continental",
    "Desserts",
    "Fast food",
    "Fried chicken",
    "Indo-Chinese",
    "Italian",
    "Kerala",
    "Malabar",
    "Mediterranean",
    "Mexican",
    "Middle Eastern",
    "Momos",
    "North Indian",
    "Pizza",
    "Punjabi",
    "Seafood",
    "Snacks",
    "Southeast Asian",
    "South Indian",
    "Thai",
    "Tibetan",
    "Vegetarian",
    "Yemeni",
]


class Command(BaseCommand):
    help = "Create cuisine tags and tag hotels that have those cuisines"

    def handle(self, *args, **kwargs):
        for name in CUISINES:
            tag = Tag.objects.filter(name__iexact=name).first()
            if tag is None:
                tag = Tag.objects.create(name=name)

            hotels = Hotel.objects.filter(cuisines__cuisine_name__iexact=name).distinct()
            tag.hotels.add(*hotels)

            self.stdout.write(f"{name}: tagged {hotels.count()} hotels")

        self.stdout.write(self.style.SUCCESS("Done."))
