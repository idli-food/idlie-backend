from django.contrib import admin

from .models import Archive, ArchiveItem


class ArchiveItemInline(admin.TabularInline):
    model = ArchiveItem
    extra = 0


@admin.register(Archive)
class ArchiveAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "user", "created_at"]
    search_fields = ["name"]
    inlines = [ArchiveItemInline]
