# admin.py

from django.contrib import admin
from .models import Post, PostMedia


class PostMediaInline(admin.TabularInline):
    model = PostMedia
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "like_count",
        "avg_rating",
        "composite_score",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "description",
        "user__display_name",
    )

    readonly_fields = (
        "like_count",
        "avg_rating",
        "rating_count",
        "composite_score",
        "created_at",
    )

    autocomplete_fields = ("user",)

    ordering = ("-created_at",)

    inlines = [PostMediaInline]

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "user",
                "description",
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


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "post",
        "content_type",
        "category",
        "position",
        "is_processed",
        "upload_status",
    )

    list_filter = (
        "content_type",
        "category",
        "upload_status",
        "is_processed",
    )

    ordering = ("post", "position")
