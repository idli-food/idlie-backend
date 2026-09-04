import csv
import re
from pathlib import Path

from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError

from ...models import Hotel

CITY = "Trivandrum"


def format_phone(phone):
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    if digits.startswith("91"):
        digits = digits[2:]
    return f"+91{digits}"


class Command(BaseCommand):
    help = "Load hotels into the database from restaurants.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "csv_path",
            nargs="?",
            default="restaurants.csv",
            help="Path to the CSV file (default: restaurants.csv)",
        )

    def handle(self, *args, **options):
        path = Path(options["csv_path"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        created = 0
        skipped = 0

        with path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader, start=1):
                name = (row.get("name") or "").strip()
                address = (row.get("address") or "").strip()
                if not name or not address:
                    skipped += 1
                    continue

                phone = format_phone((row.get("phone") or "").strip())

                location = None
                lat, lng = row.get("latitude"), row.get("longitude")
                if lat and lng:
                    try:
                        location = Point(float(lng), float(lat), srid=4326)
                    except (TypeError, ValueError):
                        location = None

                _, was_created = Hotel.objects.get_or_create(
                    name=name,
                    address=address,
                    defaults={
                        "city": CITY,
                        "phone_number": phone,
                        "location": location,
                        "location_link": (row.get("google_maps_url") or "").strip() or None,
                    },
                )
                if was_created:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(
            self.style.SUCCESS(f"Done. Created {created}, skipped {skipped}.")
        )
