import re
from django.core.management.base import BaseCommand
from django.db.models import Q
from hotel.models import Hotel


class Command(BaseCommand):
    help = "Fill place_id for hotels that have none, parsed from their location_link"

    def handle(self, *args, **kwargs):
        hotels = Hotel.objects.filter(Q(place_id__isnull=True) | Q(place_id=""))
        total = hotels.count()
        updated = 0

        for hotel in hotels:
            # Links look like https://www.google.com/maps/place/?q=place_id:ChIJ...
            match = re.search(r"place_id:([\w-]+)", hotel.location_link or "")
            if not match:
                self.stdout.write(self.style.WARNING(f"[{hotel.id}] {hotel.name}: no place_id in location_link, skipped"))
                continue

            hotel.place_id = match.group(1)
            hotel.save(update_fields=["place_id"])
            updated += 1
            self.stdout.write(f"[{hotel.id}] {hotel.name} -> {hotel.place_id}")

        self.stdout.write(self.style.SUCCESS(f"Done. Updated {updated} of {total} hotels."))
