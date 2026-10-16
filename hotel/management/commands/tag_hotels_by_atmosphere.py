from django.core.management.base import BaseCommand
from hotel.models import Hotel
from post.models import Tag

ATMOSPHERES = [
    "Casual",
    "Cosy",
    "Family-friendly",
    "Outdoor dining",
    "Premium",
    "Quiet",
    "Romantic",
    "Traditional",
    "Trendy",
]


class Command(BaseCommand):
    help = "Create atmosphere tags and tag hotels whose atmosphere contains them"

    def handle(self, *args, **kwargs):
        for name in ATMOSPHERES:
            tag = Tag.objects.filter(name__iexact=name).first()
            if tag is None:
                tag = Tag.objects.create(name=name)

            hotels = Hotel.objects.filter(atmosphere__icontains=name)
            tag.hotels.add(*hotels)

            self.stdout.write(f"{name}: tagged {hotels.count()} hotels")

        self.stdout.write(self.style.SUCCESS("Done."))
