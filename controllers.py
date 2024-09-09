import tkinter as tk
from tkinter import messagebox
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from models import JobApplication
from database import insert_application, update_application, delete_application
from datetime import datetime


def add_or_update_application(tree, company_entry, position_entry, date_applied_entry, status_combo,
                              notes_entry, reminder_date_entry, location_entry, update_table, clear_entries):
    company = company_entry.get().strip()
    position = position_entry.get().strip()
    date_applied = date_applied_entry.get().strip()
    status = status_combo.get()
    notes = notes_entry.get().strip()
    reminder_date = reminder_date_entry.get().strip()
    location = location_entry.get().strip()

    if location and not validate_location(location):
        tk.messagebox.showerror("Invalid Location", "The provided location is not valid.")
        return

    if not company or not position:
        messagebox.showwarning("Input Error", "Company and Position are required fields.")
        return

    # Set today's date as default if no date is entered
    if not date_applied:
        date_applied = datetime.now().strftime('%Y-%m-%d')
    elif not validate_date(date_applied):
        messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
        return

    new_app = JobApplication(company, position, date_applied, status, notes, reminder_date, location)

    selected_items = tree.selection()
    if selected_items:
        # Update existing application
        item = selected_items[0]
        app_id = tree.item(item, "values")[0]
        new_app.id = app_id  # Set the ID for the existing application
        update_application(app_id, new_app)
    else:
        # Add new application
        insert_application(new_app)

    update_table()
    clear_entries()


def edit_selected(tree, company_entry, position_entry, date_applied_entry, status_combo, notes_entry,
                  reminder_date_entry, location_entry):
    selected_items = tree.selection()
    if selected_items:
        item = selected_items[0]
        values = tree.item(item)['values']
        company_entry.delete(0, tk.END)
        company_entry.insert(0, values[1])
        position_entry.delete(0, tk.END)
        position_entry.insert(0, values[2])
        date_applied_entry.delete(0, tk.END)
        date_applied_entry.insert(0, values[3])
        status_combo.set(values[4])
        notes_entry.delete(0, tk.END)
        notes_entry.insert(0, values[5])
        reminder_date_entry.delete(0, tk.END)
        reminder_date_entry.insert(0, values[6])
        location_entry.delete(0, tk.END)
        location_entry.insert(0, values[7])

    else:
        messagebox.showinfo("Selection", "Please select an application to edit.")


def delete_selected(tree, update_table):
    selected_items = tree.selection()
    if selected_items:
        if messagebox.askyesno("Delete", "Are you sure you want to delete the selected application?"):
            item = selected_items[0]
            app_id = tree.item(item, "values")[0]
            delete_application(app_id)
            update_table()
    else:
        messagebox.showinfo("Selection", "Please select an application to delete.")


def validate_date(date_string):
    import re
    from datetime import datetime
    if not date_string:
        return True  # Allow empty date
    pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    if not pattern.match(date_string):
        return False
    try:
        datetime.strptime(date_string, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_location(location):
    geolocator = Nominatim(user_agent="job_application_tracker")
    try:
        location_info = geolocator.geocode(location)
        if location_info:
            return True
        else:
            return False
    except (GeocoderTimedOut, GeocoderUnavailable):
        return False