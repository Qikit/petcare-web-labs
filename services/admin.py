from django.contrib import admin

from .models import Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_minutes', 'specialty', 'is_active')
    list_display_links = ('name',)
    list_filter = ('is_active', 'specialty')
    search_fields = ('name', 'description')
