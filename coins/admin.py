from django.contrib import admin

from .models import Coins


@admin.register(Coins)
class CoinsAdmin(admin.ModelAdmin):
    list_display = ('user', 'count')
    search_fields = ('user__username', 'user__phone')
    ordering = ('-count',)
