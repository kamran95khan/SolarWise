# ☀ SolarWise – Smart Solar Energy Planning

## Overview

SolarWise is a web-based solar energy planning application developed using Python, Django, JavaScript, HTML, and CSS.

The purpose of SolarWise is to help users estimate their solar panel requirements, calculate battery backup, estimate solar project costs, and manage their solar projects.

Users can create an account, use the calculators, save their projects, edit or delete saved projects, and download project reports in PDF format.

## Distinctiveness and Complexity

SolarWise is different from the social networking applications developed in the earlier CS50 Web projects. It is designed as a practical solar energy planning tool.

The project combines multiple features into one application, including solar panel calculations, battery backup calculations, project cost estimation, user authentication, project management, and PDF report generation.

The application uses Django models and database relationships to store solar project information. Each project is associated with its owner, and users can manage their own saved projects.

The project also uses JavaScript alongside Django and HTML/CSS to provide frontend functionality.

## Features

- User registration and login.
- Solar panel requirement calculator.
- Battery backup calculator.
- Solar project cost calculator.
- Save solar projects.
- View saved projects.
- Edit existing projects.
- Delete projects.
- Download project reports in PDF format.
- User-specific project management.
- Admin panel for project administration.

## Solar Calculator Assumptions

The solar panel calculator uses the following assumptions:

- 30 days per month.
- 5 peak sun-hours per day.
- 80% system efficiency.

These assumptions are used to estimate the required solar capacity and number of solar panels.

Actual solar system requirements may vary depending on location, weather, equipment, and electricity consumption.

## Technologies Used

- Python
- Django 6.1
- JavaScript
- HTML5
- CSS3
- SQLite
- ReportLab
- Pillow

## Installation and Setup

Follow these steps to run SolarWise locally.

### 1. Clone or Download the Project

Download the project and open its folder in the terminal.

### 2. Create a Virtual Environment

python -m venv .venv

### 3. Activate the Virtual Environment

For Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

python -m pip install -r requirements.txt


### 5. Apply Database Migrations

python manage.py migrate

### 6. Start the Development Server

python manage.py runserver


### 7. Open the Application

Visit the following address in your browser:


http://127.0.0.1:8000/


## Project Structure

solarwise/
│
├── manage.py
├── requirements.txt
├── README.md
├── db.sqlite3
│
├── solarwise