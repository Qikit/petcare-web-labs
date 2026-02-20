from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'show_pets_count')
    list_display_links = ('email', 'first_name')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('date_joined', 'last_login')
    filter_horizontal = ('groups', 'user_permissions')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Права', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('email', 'password1', 'password2', 'role')}),
    )

    @admin.display(description='Кол-во питомцев')
    def show_pets_count(self, obj):
        return obj.pets.count()
