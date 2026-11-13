
import math
from xml.sax.saxutils import escape

from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import F, ExpressionWrapper, FloatField
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

from .models import SolarProject


# ==========================================
# HOME PAGE
# ==========================================

def home(request):
    projects = []

    if request.user.is_authenticated:
        projects = SolarProject.objects.filter(
            user=request.user
        ).annotate(
            monthly_units=ExpressionWrapper(
                F("daily_usage") * 30,
                output_field=FloatField()
            )
        ).order_by("-created_at")

    return render(
        request,
        "planner/home.html",
        {"projects": projects}
    )


# ==========================================
# SIGNUP PAGE
# ==========================================

def signup(request):

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            auth_login(request, user)

            messages.success(
                request,
                "Your account has been created successfully!"
            )

            return redirect("home")

    else:
        form = UserCreationForm()

    return render(
        request,
        "planner/signup.html",
        {"form": form}
    )


# ==========================================
# SOLAR CALCULATOR
# ==========================================

def solar_calculator(request):

    context = {}

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

        except (ValueError, TypeError, OverflowError):

            messages.error(
                request,
                "Please enter valid electricity units and panel wattage."
            )

            return redirect("solar_calculator")

        daily_usage = monthly_units / 30

        required_kw = daily_usage / (5 * 0.80)

        panel_quantity = math.ceil(
            required_kw * 1000 / panel_watt
        )

        solar_capacity = (
            panel_quantity * panel_watt / 1000
        )

        context = {
            "monthly_units": monthly_units,
            "daily_usage": round(daily_usage, 2),
            "required_kw": round(required_kw, 2),
            "panel_watt": panel_watt,
            "panel_quantity": panel_quantity,
            "solar_capacity": round(solar_capacity, 3),
            "calculated": True,
        }

        if "save_project" in request.POST:

            if not request.user.is_authenticated:

                messages.error(
                    request,
                    "Please login before saving your project."
                )

                return redirect("login")

            project_name = request.POST.get(
                "project_name",
                "My Solar Project"
            ).strip()[:100]

            if not project_name:
                project_name = "My Solar Project"

            SolarProject.objects.create(
                user=request.user,
                name=project_name,
                daily_usage=daily_usage,
                peak_load=required_kw,
                panel_watt=panel_watt,
                panel_quantity=panel_quantity,
                solar_capacity=solar_capacity,
                battery_voltage=48,
                battery_type="lithium",
                battery_backup_hours=6,
                battery_load_kw=3,
                battery_unit_capacity_ah=100,
                battery_capacity=0,
                battery_quantity=0,
                inverter_capacity=0,
                estimated_cost=0,
            )

            messages.success(
                request,
                "Your solar project has been saved successfully!"
            )

            return redirect("home")

    return render(
        request,
        "planner/calculator.html",
        context
    )


# ==========================================
# BATTERY AND INVERTER CALCULATOR
# ==========================================

@login_required
def battery_calculator(request):

    projects = SolarProject.objects.filter(
        user=request.user
    ).order_by("-created_at")

    context = {
        "projects": projects,
        "default_load": 3,
        "default_backup": 6,
        "default_voltage": 48,
        "default_battery_ah": 100,
    }

    if request.method == "POST":

        try:
            project_id = int(
                request.POST.get("project_id", 0)
            )

            load_kw = float(
                request.POST.get("load_kw", 3)
            )

            backup_hours = float(
                request.POST.get("backup_hours", 6)
            )

            battery_ah = float(
                request.POST.get("battery_ah", 100)
            )

            if (
                not math.isfinite(load_kw)
                or not math.isfinite(backup_hours)
                or not math.isfinite(battery_ah)
                or load_kw <= 0
                or load_kw > 100
                or backup_hours <= 0
                or backup_hours > 24
                or battery_ah <= 0
                or battery_ah > 1000
            ):
                raise ValueError

        except (ValueError, TypeError, OverflowError):

            messages.error(
                request,
                "Please enter valid battery calculator values."
            )

            return redirect("battery_calculator")

        project = get_object_or_404(
            SolarProject,
            id=project_id,
            user=request.user
        )

        battery_voltage = 48

        # Battery calculation assumptions
        usable_depth = 0.80
        inverter_efficiency = 0.90

        required_energy = load_kw * backup_hours

        one_battery_capacity = (
            battery_voltage * battery_ah / 1000
        )

        usable_energy_per_battery = (
            one_battery_capacity
            * usable_depth
            * inverter_efficiency
        )

        battery_quantity = math.ceil(
            required_energy / usable_energy_per_battery
        )

        total_battery_capacity = (
            battery_quantity * one_battery_capacity
        )

        # Select a standard inverter size
        recommended_load = load_kw * 1.25

        standard_inverters = [
            1, 1.5, 2, 3, 3.5, 5, 6, 8, 10,
            12, 15, 20, 25, 30, 40, 50, 60,
            80, 100
        ]

        inverter_capacity = next(
            (
                size for size in standard_inverters
                if size >= recommended_load
            ),
            math.ceil(recommended_load)
        )

        # Save battery and inverter information
        project.battery_voltage = battery_voltage
        project.battery_type = "lithium"
        project.battery_backup_hours = backup_hours
        project.battery_load_kw = load_kw
        project.battery_unit_capacity_ah = battery_ah
        project.battery_capacity = total_battery_capacity
        project.battery_quantity = battery_quantity
        project.inverter_capacity = inverter_capacity

        project.save()

        context.update({
            "calculated": True,
            "selected_project": project,
            "load_kw": load_kw,
            "backup_hours": backup_hours,
            "battery_ah": battery_ah,
            "battery_voltage": battery_voltage,
            "required_energy": round(required_energy, 2),
            "battery_quantity": battery_quantity,
            "one_battery_capacity": round(
                one_battery_capacity, 2
            ),
            "total_battery_capacity": round(
                total_battery_capacity, 2
            ),
            "inverter_capacity": inverter_capacity,
        })

        messages.success(
            request,
            "Battery and inverter details saved successfully!"
        )

    return render(
        request,
        "planner/battery_calculator.html",
        context
    )


# ==========================================
# EDIT PROJECT
# ==========================================

@login_required
def edit_project(request, project_id):

    project = get_object_or_404(
        SolarProject,
        id=project_id,
        user=request.user
    )

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

        except (ValueError, TypeError, OverflowError):

            messages.error(
                request,
                "Please enter valid electricity units and panel wattage."
            )

            return redirect(
                "edit_project",
                project_id=project.id
            )

        daily_usage = monthly_units / 30

        required_kw = daily_usage / (5 * 0.80)

        panel_quantity = math.ceil(
            required_kw * 1000 / panel_watt
        )

        solar_capacity = (
            panel_quantity * panel_watt / 1000
        )

        project_name = request.POST.get(
            "project_name",
            project.name
        ).strip()[:100]

        if not project_name:
            project_name = "My Solar Project"

        project.name = project_name
        project.daily_usage = daily_usage
        project.peak_load = required_kw
        project.panel_watt = panel_watt
        project.panel_quantity = panel_quantity
        project.solar_capacity = solar_capacity

        project.save()

        messages.success(
            request,
            "Your solar project has been updated successfully!"
        )

        return redirect("home")

    monthly_units = project.daily_usage * 30

    return render(
        request,
        "planner/edit_project.html",
        {
            "project": project,
            "monthly_units": monthly_units,
        }
    )


# ==========================================
# DELETE PROJECT
# ==========================================

@login_required
def delete_project(request, project_id):

    project = get_object_or_404(
        SolarProject,
        id=project_id,
        user=request.user
    )

    if request.method == "POST":

        project.delete()

        messages.success(
            request,
            "Your solar project has been deleted successfully!"
        )

        return redirect("home")

    return render(
        request,
        "planner/delete_project.html",
        {"project": project}
    )


# ==========================================
# PROJECT COST CALCULATOR
# ==========================================

@login_required
def project_cost(request):

    projects = SolarProject.objects.filter(
        user=request.user
    ).order_by("-created_at")

    context = {
        "projects": projects,
    }

    if request.method == "POST":

        try:
            project_id = int(
                request.POST.get("project_id", 0)
            )

            panel_price = float(
                request.POST.get("panel_price", 0)
            )

            battery_price = float(
                request.POST.get("battery_price", 0)
            )

            inverter_price = float(
                request.POST.get("inverter_price", 0)
            )

            structure_cost = float(
                request.POST.get("structure_cost", 0)
            )

            wiring_cost = float(
                request.POST.get("wiring_cost", 0)
            )

            labour_cost = float(
                request.POST.get("labour_cost", 0)
            )

            prices = [
                panel_price,
                battery_price,
                inverter_price,
                structure_cost,
                wiring_cost,
                labour_cost,
            ]

            if any(
                not math.isfinite(price)
                or price < 0
                or price > 100000000
                for price in prices
            ):
                raise ValueError

        except (ValueError, TypeError, OverflowError):

            messages.error(
                request,
                "Please enter valid project prices."
            )

            return redirect("project_cost")

        project = get_object_or_404(
            SolarProject,
            id=project_id,
            user=request.user
        )

        panel_total = (
            project.panel_quantity * panel_price
        )

        battery_total = (
            project.battery_quantity * battery_price
        )

        total_cost = (
            panel_total
            + battery_total
            + inverter_price
            + structure_cost
            + wiring_cost
            + labour_cost
        )

        project.estimated_cost = total_cost
        project.save()

        context.update({
            "calculated": True,
            "selected_project": project,
            "panel_total": panel_total,
            "battery_total": battery_total,
            "inverter_price": inverter_price,
            "structure_cost": structure_cost,
            "wiring_cost": wiring_cost,
            "labour_cost": labour_cost,
            "total_cost": total_cost,
        })

        messages.success(
            request,
            "Project cost calculated and saved successfully!"
        )

    return render(
        request,
        "planner/project_cost.html",
        context
    )


# ==========================================
# DOWNLOAD PROJECT PDF REPORT
# ==========================================

@login_required
def download_project_pdf(request, project_id):

    project = get_object_or_404(
        SolarProject,
        id=project_id,
        user=request.user
    )

    response = HttpResponse(
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="SolarWise_Project_{project.id}.pdf"'
    )

    pdf = SimpleDocTemplate(
        response,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(
        Paragraph(
            "SolarWise - Solar Project Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(
        Paragraph(
            "Project Name: " + escape(project.name),
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            "Report Date: " + project.created_at.strftime("%d %B %Y"),
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 0.3 * inch))

    data = [
        ["Project Details", "Value"],
        ["Daily Electricity Usage", f"{project.daily_usage:.2f} kWh"],
        ["Monthly Electricity Units", f"{project.daily_usage * 30:.2f} kWh"],
        ["Panel Wattage", f"{project.panel_watt} W"],
        ["Panel Quantity", str(project.panel_quantity)],
        ["Solar Capacity", f"{project.solar_capacity:.2f} kW"],
        ["Battery Type", project.battery_type.title()],
        ["Battery Voltage", f"{project.battery_voltage} V"],
        ["Battery Quantity", str(project.battery_quantity)],
        ["Battery Capacity", f"{project.battery_capacity:.2f} kWh"],
        ["Battery Backup", f"{project.battery_backup_hours:.1f} Hours"],
        ["Backup Load", f"{project.battery_load_kw:.2f} kW"],
        ["Battery Unit Capacity", f"{project.battery_unit_capacity_ah:.0f} Ah"],
        ["Inverter Capacity", f"{project.inverter_capacity:.2f} kW"],
        ["Estimated Total Cost", f"PKR {project.estimated_cost:,.2f}"],
    ]

    table = Table(
        data,
        colWidths=[3.3 * inch, 2.5 * inch]
    )

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.darkgreen),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("PADDING", (0, 0), (-1, -1), 9),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
        ])
    )

    elements.append(table)

    elements.append(Spacer(1, 0.4 * inch))

    elements.append(
        Paragraph(
            "Generated by SolarWise - Smart Solar Energy Planning",
            styles["Italic"]
        )
    )

    pdf.build(elements)

    return response
