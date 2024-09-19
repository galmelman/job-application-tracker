import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from database import get_all_applications
from tkinter import messagebox
import pandas as pd
import numpy as np
import json, os


def load_settings(file_path='settings.json'):
    default_settings = {
        "theme": "solar",
        "default_status": "Applied",
        "email": "",
        "mailing_enabled": False
    }

    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            loaded_settings = json.load(file)
            default_settings.update(loaded_settings)

    return default_settings


def check_email_feature_enabled(settings):
    return settings.get('email_reminders', False)


def check_reminders(applications, settings):
    today = datetime.now().date()
    email_feature_enabled = settings.get('mailing_enabled', False)

    for app in applications:
        if app.reminder_date and not app.status == 'Rejected' and datetime.strptime(app.reminder_date, "%Y-%m-%d").date() < today:
            if email_feature_enabled:
                send_email_reminder(app, settings)
            show_reminder_popup(app)


def send_email_reminder(application, settings):
    # Email credentials
    sender_email = "jobapplicationtracker1@outlook.com"
    password = "nokhzmittoyrycyg"

    # Retrieve email settings
    receiver_email = settings.get('email', 'example@gmail.com')

    # Create the email content
    subject = f"Follow-up Reminder: {application.position} at {application.company}"
    body = (
        f"Hello,\n\nThis is a reminder to follow up on your job application for the "
        f"position of {application.position} at {application.company}. "
        f"You applied on {application.date_applied}.\n\nBest regards,\nJob Application Tracker"
    )

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Set up the SMTP server
        server = smtplib.SMTP('smtp-mail.outlook.com', 587)
        server.starttls()
        server.login(sender_email, password)

        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        print(f"Email reminder sent for application to {application.position}!")
    except Exception as e:
        print(f"Failed to send email reminder: {e}")


def show_reminder_popup(application):
    messagebox.showinfo("Reminders", f"Follow up your application to {application.company} for the {application.position} position.")


def setup_reminder_check(master, applications, settings):
    check_reminders(applications, settings)
    master.after(86400000, lambda: setup_reminder_check(master, applications,settings))  # Check every 24 hours


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
        'applications_per_month': df['month_year'].value_counts().sort_index().to_dict(),
    }

    # Calculate average applications per month
    months_count = df['month_year'].nunique()
    statistics['avg_applications_per_month'] = len(applications) / months_count if months_count > 0 else 0

    # Most applied company
    statistics['most_applied_company'] = df['company'].mode().iloc[0] if not df['company'].empty else "N/A"

    # Most common position
    statistics['most_common_position'] = df['position'].mode().iloc[0] if not df['position'].empty else "N/A"

    # Success rate (considering 'Offer Received' as success)
    success_count = df[df['status'] == 'Offer Received'].shape[0]
    statistics['success_rate'] = (success_count / len(applications)) * 100 if len(applications) > 0 else 0

    # Average response time (considering 'Interview Scheduled' or 'Offer Received' as response)
    df['response_time'] = np.where(
        df['status'].isin(['Interview Scheduled', 'Offer Received']),
        (datetime.now() - df['date_applied']).dt.days,
        np.nan
    )
    statistics['avg_response_time'] = df['response_time'].mean()

    return statistics
