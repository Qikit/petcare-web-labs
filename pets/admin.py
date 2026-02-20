from django.contrib import admin

from .models import Pet


@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'breed', 'owner', 'age', 'created_at')
    list_display_links = ('name',)
    list_filter = ('species',)
    search_fields = ('name', 'breed', 'owner__email', 'owner__last_name')
    raw_id_fields = ('owner',)
    readonly_fields = ('created_at',)
