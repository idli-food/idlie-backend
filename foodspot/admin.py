# admin.py

from django.contrib import admin
from .models import FoodSpot


@admin.register(FoodSpot)
class FoodSpotAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "address",
        "created_by",
        "is_verified",
        "created_at",
    )

    list_filter = (
        "is_verified",
        "created_at",
    )

    search_fields = (
        "name",
        "address",
        "google_place_id",
        "created_by__display_name",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = ("created_by",)

    ordering = ("-created_at",)

    fieldsets = (
        ("Basic Info", {
            "fields": (
                "name",
                "address",
                "google_place_id",
            )
        }),

        ("Location", {
            "fields": ("location",)
        }),

        ("Meta", {
            "fields": (
                "created_by",
                "is_verified",
                "created_at",
            )
        }),
    )