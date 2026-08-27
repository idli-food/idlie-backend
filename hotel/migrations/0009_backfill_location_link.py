import csv
from pathlib import Path

from django.conf import settings
from django.db import migrations


def forwards(apps, schema_editor):
    Hotel = apps.get_model("hotel", "Hotel")

    path = Path(settings.BASE_DIR) / "restaurants.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get("name") or "").strip()
            address = (row.get("address") or "").strip()
            if not name or not address:
                continue

            link = (row.get("google_maps_url") or "").strip()
            if not link:
                continue

            Hotel.objects.filter(name=name, address=address).update(
                location_link=link
            )


class Migration(migrations.Migration):

    dependencies = [
        ("hotel", "0008_hotel_location_link"),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
