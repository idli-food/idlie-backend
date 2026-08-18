from django.contrib import admin

from .models import Hotel


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone_number", "email", "created_at")
    search_fields = ("name", "city", "email", "phone_number")
