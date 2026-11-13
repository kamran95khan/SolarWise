
from django.db import models
from django.contrib.auth.models import User


class SolarProject(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="solar_projects"
    )

    name = models.CharField(max_length=100)

    # Load information
    daily_usage = models.FloatField(default=0)
    peak_load = models.FloatField(default=0)

    # Solar panel information
    panel_watt = models.IntegerField(default=550)
    panel_quantity = models.IntegerField(default=0)
    solar_capacity = models.FloatField(default=0)

    # Battery system information
    battery_voltage = models.IntegerField(default=48)
    battery_type = models.CharField(
        max_length=20,
        default="lithium"
    )
    battery_backup_hours = models.FloatField(default=6)
    battery_load_kw = models.FloatField(default=3)
    battery_unit_capacity_ah = models.FloatField(default=100)

    # Total battery capacity in kWh
    battery_capacity = models.FloatField(default=0)
    battery_quantity = models.IntegerField(default=0)

    # Inverter information
    inverter_capacity = models.FloatField(default=0)

    # Cost estimation
    estimated_cost = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
