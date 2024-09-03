import csv
from models import JobApplication
from datetime import datetime
import tkinter as tk
from tkinter import messagebox


def check_reminders(applications):
    today = datetime.now().date()
    for app in applications:
        if app.reminder_date and datetime.strptime(app.reminder_date, "%Y-%m-%d").date() < today:
            show_reminder_popup(app)

def show_reminder_popup(application):
    messagebox.showinfo("Reminders", f"Follow up your application to {application.company} for the {application.position} position.")

def setup_reminder_check(master,applications):
    check_reminders(applications)
    master.after(60000, lambda: setup_reminder_check(master, applications))  # Check every 24 hours
#86400000

def save_applications(filename, applications):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Company", "Position", "Date Applied", "Status", "Notes", "Reminder Date"])
        for app in applications:
            writer.writerow([app.company, app.position, app.date_applied, app.status, app.notes, app.reminder_date])


def load_applications(filename):
    applications = []
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            next(reader)  # Skip header
            for row in reader:
                applications.append(JobApplication(*row))
    except FileNotFoundError:
        pass
    return applications
