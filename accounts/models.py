from django.db import models

from user.models import User
from post.models import Post


class Archive(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="archives",
    )
    name = models.CharField(max_length=100)
    emoji = models.CharField(max_length=16, blank=True)
    cover_url = models.URLField(max_length=2000, blank=True)
    posts = models.ManyToManyField(
        Post,
        through="ArchiveItem",
        related_name="archives",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Archive {self.id} ({self.name})"


class ArchiveItem(models.Model):
    archive = models.ForeignKey(
        Archive,
        on_delete=models.CASCADE,
        related_name="items",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="archive_items",
    )
    position = models.PositiveIntegerField(default=0)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["position", "added_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["archive", "post"],
                name="uniq_archive_post",
            ),
        ]
