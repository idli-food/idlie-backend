from urllib.parse import quote_plus
from django.core.management.base import BaseCommand
from hotel.models import Hotel


class Command(BaseCommand):
    help = "Overwrite location_link with a Google Maps link built from the hotel's place_id"

    def handle(self, *args, **kwargs):
        hotels = Hotel.objects.exclude(place_id__isnull=True).exclude(place_id="")
        total = hotels.count()

        for hotel in hotels:
            hotel.location_link = (
                "https://www.google.com/maps/search/?api=1"
                f"&query={quote_plus(hotel.name)}&query_place_id={hotel.place_id}"
            )
            hotel.save(update_fields=["location_link"])
            self.stdout.write(f"[{hotel.id}] {hotel.name} -> {hotel.location_link}")

        self.stdout.write(self.style.SUCCESS(f"Done. Updated {total} hotels."))
