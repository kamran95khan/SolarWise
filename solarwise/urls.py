
from django.contrib import admin
from django.urls import path, include
from planner import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),

    path(
        "calculator/",
        views.solar_calculator,
        name="solar_calculator"
    ),

    path(
        "battery-calculator/",
        views.battery_calculator,
        name="battery_calculator"
    ),

    path(
        "project-cost/",
        views.project_cost,
        name="project_cost"
    ),

    path(
        "signup/",
        views.signup,
        name="signup"
    ),

    path(
        "accounts/",
        include("django.contrib.auth.urls")
    ),

    path(
        "project/<int:project_id>/edit/",
        views.edit_project,
        name="edit_project"
    ),

    path(
        "project/<int:project_id>/delete/",
        views.delete_project,
        name="delete_project"
    ),

    path(
        "project/<int:project_id>/pdf/",
        views.download_project_pdf,
        name="download_project_pdf"
    ),
]
