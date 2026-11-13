
import math

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from .models import SolarProject


def home(request):
    projects = []

    if request.user.is_authenticated:
        projects = SolarProject.objects.filter(
            user=request.user
        ).order_by("-created_at")

    return render(
        request,
        "planner/home.html",
        {"projects": projects},
    )


def solar_calculator(request):
    context = {
        "monthly_units": "",
        "panel_watt": 615,
    }

    if request.method == "POST":
        try:
            monthly_units = float(
                request.POST.get("monthly_units", 0)
            )
            panel_watt = int(
                request.POST.get("panel_watt", 615)
            )

            if (
                not math.isfinite(monthly_units)
                or monthly_units <= 0
                or monthly_units > 100000
                or panel_watt <= 0
                or panel_watt > 2000
            ):
                raise ValueError

            daily_usage = monthly_units / 30

            # Estimate using 5 peak-sun-hours and 80% efficiency.
            required_kw = daily_usage / (5 * 0.80)

            panel_quantity = math.ceil(
                required_kw * 1000 / panel_watt
            )

            solar_capacity = (
                panel_quantity * panel_watt / 1000
            )

            context.update({
                "monthly_units": monthly_units,
                "panel_watt": panel_watt,
                "daily_usage": round(daily_usage, 2),
                "required_kw": round(required_kw, 2),
                "panel_quantity": panel_quantity,
                "solar_capacity": round(solar_capacity, 3),
                "calculated": True,
            })

            if "save_project" in request.POST:
                if not request.user.is_authenticated:
                    messages.error(
                        request,
                        "Project save karne ke liye pehle login karein.",
                    )
                    return redirect("login")

                project_name = (
                    request.POST.get(
                        "project_name", ""
                    ).strip()
                    or "My Solar Project"
                )[:100]

                SolarProject.objects.create(
                    user=request.user,
                    name=project_name,
                    daily_usage=daily_usage,
                    peak_load=0,
                    panel_watt=panel_watt,
                    panel_quantity=panel_quantity,
                    solar_capacity=solar_capacity,
                    battery_voltage=48,
                    battery_capacity=0,
                    battery_quantity=0,
                    inverter_capacity=0,
                    estimated_cost=0,
                )

                messages.success(
                    request,
                    "Solar project successfully save ho gaya!",
                )
                return redirect("home")

        except (ValueError, TypeError, OverflowError):
            context["error"] = (
                "Please valid monthly units aur panel watt enter karein."
            )

    return render(
        request,
        "planner/calculator.html",
        context,
    )


def signup(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                "SolarWise account successfully create ho gaya!",
            )
            return redirect("home")
    else:
        form = UserCreationForm()

    return render(
        request,
        "planner/signup.html",
        {"form": form},
    )
