# admin.py

from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "user",
        "food_spot",
        "media_type",
        "status",
        "like_count",
        "avg_rating",
        "composite_score",
        "is_proccessed",
        "created_at",
    )

    list_filter = (
        "media_type",
        "status",
        "is_proccessed",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "user__display_name",
        "food_spot__name",
    )

    readonly_fields = (
        "like_count",
        "avg_rating",
        "rating_count",
        "composite_score",
        "created_at",
    )

    autocomplete_fields = ("user", "food_spot")

    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "user",
                "food_spot",
                "foodspot_tag",
                "title",
                "description",
            )
        }),

        ("Media", {
            "fields": (
                "media_type",
                "raw_s3_key",
                "media_url",
                "thumbnail_url",
                "is_proccessed",
            )
        }),

        ("Status & Metrics", {
            "fields": (
                "status",
                "like_count",
                "avg_rating",
                "rating_count",
                "composite_score",
            )
        }),

        ("Location", {
            "fields": ("location",)
        }),

        ("Timestamps", {
            "fields": ("created_at",)
        }),
    )