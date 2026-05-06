
# Register your models here.
from django.contrib import admin
from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'phone',
        'first_name',
        'last_name',
        'diet',
        'credibility_score',
        'created_at',
    )

    search_fields = (
        'username',
        'phone',
        'first_name',
        'last_name',
    )

    list_filter = (
        'diet',
        'created_at',
    )

    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'username',
                'phone',
                'first_name',
                'last_name',
                'dob',
            )
        }),
        ('Profile', {
            'fields': (
                'bio',
                'avatar_url',
                'diet',
                'food_preference',
            )
        }),
        ('Metrics', {
            'fields': (
                'credibility_score',
                'created_at',
            )
        }),
    )