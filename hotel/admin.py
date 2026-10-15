from django.contrib import admin

from .models import Hotel, HotelCuisine, HotelService, HotelFacility, HotelDish


class HotelDishInline(admin.TabularInline):
    model = HotelDish
    extra = 0


class HotelCuisineInline(admin.TabularInline):
    model = HotelCuisine
    extra = 0


class HotelServiceInline(admin.TabularInline):
    model = HotelService
    extra = 0


class HotelFacilityInline(admin.TabularInline):
    model = HotelFacility
    extra = 0


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "phone_number", "email", "created_at")
    search_fields = ("name", "city", "email", "phone_number")
    filter_horizontal = ("tags",)
    inlines = [HotelDishInline, HotelCuisineInline, HotelServiceInline, HotelFacilityInline]
