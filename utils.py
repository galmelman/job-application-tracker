import csv
from models import JobApplication
from datetime import datetime
from database import get_all_applications
from tkinter import messagebox
import pandas as pd


def check_reminders(applications):
    today = datetime.now().date()
    for app in applications:
        if app.reminder_date and datetime.strptime(app.reminder_date, "%Y-%m-%d").date() < today:
            show_reminder_popup(app)


def show_reminder_popup(application):
    messagebox.showinfo("Reminders", f"Follow up your application to {application.company} for the {application.position} position.")


def setup_reminder_check(master,applications):
    check_reminders(applications)
    master.after(86400000, lambda: setup_reminder_check(master, applications))  # Check every 24 hours


def get_application_statistics():
    applications = get_all_applications()
    df = pd.DataFrame([app.__dict__ for app in applications])

    # Convert 'date_applied' to datetime format
    df['date_applied'] = pd.to_datetime(df['date_applied'], errors='coerce')

    # Extract month and year
    df['month_year'] = df['date_applied'].dt.to_period('M')

    statistics = {
        'total_applications': len(applications),
        'applications_per_status': df['status'].value_counts().to_dict(),
        'applications_per_company': df['company'].value_counts().to_dict(),
        'applications_per_position': df['position'].value_counts().to_dict(),
        'applications_per_month': df['month_year'].value_counts().to_dict(),
    }

    return statistics
