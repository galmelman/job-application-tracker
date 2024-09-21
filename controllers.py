import tkinter as tk
from tkinter import messagebox
from geopy import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable
from models import JobApplication
from database import insert_application, update_application, delete_application
from datetime import datetime


def add_or_update_application(self):
    company = self.company_entry.get().strip()
    position = self.position_entry.get().strip()
    date_applied = self.date_applied_picker.get()
    status = self.status_combo.get()
    notes = self.notes_entry.get().strip() if hasattr(self, 'notes_entry') else ""
    reminder_date = self.reminder_date_picker.get()
    location = self.location_entry.get().strip()
    salary_offered = self.salary_entry.get().strip() if hasattr(self, 'salary_entry') else None
    job_description = self.job_description_entry.get().strip() if hasattr(self, 'job_description_entry') else ""
    company_culture = self.company_culture_entry.get().strip() if hasattr(self, 'company_culture_entry') else ""
    interviewer_names = self.interviewer_names_entry.get().strip() if hasattr(self, 'interviewer_names_entry') else ""

    if location and not validate_location(location):
        tk.messagebox.showerror("Invalid Location", "The provided location is not valid.")
        return

    if not company or not position:
        messagebox.showwarning("Input Error", "Company and Position are required fields.")
        return

    if not date_applied:
        date_applied = datetime.now().strftime('%Y-%m-%d')
    elif not validate_date(date_applied):
        messagebox.showwarning("Input Error", "Invalid date format. Please use YYYY-MM-DD.")
        return

    if reminder_date and not validate_date(reminder_date):
        messagebox.showwarning("Input Error", "Invalid reminder date format. Please use YYYY-MM-DD.")
        return

    new_app = JobApplication(company, position, date_applied, status, notes, reminder_date, location)
    new_app.salary_offered = float(salary_offered) if salary_offered else None
    new_app.job_description = job_description
    new_app.company_culture = company_culture
    new_app.interviewer_names = interviewer_names

    if hasattr(self, 'app_id'):
        # Update existing application
        new_app.id = self.app_id
        update_application(self.app_id, new_app)
        messagebox.showinfo("Success", "Application updated successfully.")
    else:
        # Add new application
        insert_application(new_app)
        messagebox.showinfo("Success", "Application added successfully.")

    if hasattr(self, 'update_callback'):
        self.update_callback()
    self.window.destroy()

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


def check_date(event):
    entered_date = event.widget.get()

    # Validate the entered date
    if not validate_date(entered_date):
        messagebox.showerror("Invalid Date", "Please enter a valid date (YYYY-MM-DD).")
        #event.widget.delete(0, tk.END)  # Clear the invalid input
        event.widget.focus()  # Set focus back to the date entry



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