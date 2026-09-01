
# Register your models here.
from django.contrib import admin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'phone',
        'first_name',
        'last_name',
        'created_at',
    )

    search_fields = (
        'username',
        'phone',
        'first_name',
        'last_name',
    )

    list_filter = ('created_at',)

    ordering = ('-created_at',)

    readonly_fields = ('created_at',)

    fieldsets = (
        ('Basic Information', {
            'fields': (
                'username',
                'phone',
                'first_name',
                'last_name',
            )
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'diet', 'credibility_score', 'is_verified')
    list_filter = ('diet', 'is_verified')
    search_fields = ('user__username', 'user__phone')