from django.contrib import admin

from core.models import Waitlister


@admin.register(Waitlister)
class WaitlisterAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email")
