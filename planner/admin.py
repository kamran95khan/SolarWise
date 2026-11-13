from django.contrib import admin
from .models import SolarProject


@admin.register(SolarProject)
class SolarProjectAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'user',
        'solar_capacity',
        'panel_quantity',
        'battery_quantity',
        'inverter_capacity',
        'estimated_cost',
        'created_at',
    )

    list_filter = (
        'created_at',
        'battery_voltage',
    )

    search_fields = (
        'name',
        'user__username',
    )

    ordering = ('-created_at',)