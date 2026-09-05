from django.core.management.base import BaseCommand
from django.db.models import F, Q
from post.models import PostMedia

DEFAULT_PLACEHOLDER = "http://125.0.0.00"


class Command(BaseCommand):
    help = "Backfill thumbnail_url = media_url for image posts missing a real thumbnail"

    def handle(self, *args, **kwargs):
        qs = PostMedia.objects.filter(
            content_type=PostMedia.ContentType.IMAGE,
        ).filter(
            Q(thumbnail_url__isnull=True)
            | Q(thumbnail_url="")
            | Q(thumbnail_url=DEFAULT_PLACEHOLDER)
        )

        count = qs.count()
        updated = qs.update(thumbnail_url=F("media_url"))

        self.stdout.write(
            self.style.SUCCESS(f"Updated {updated} of {count} image media.")
        )
